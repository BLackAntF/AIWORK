from datetime import datetime, date
from flask import request
from sqlalchemy import func
from routes.admin import admin_bp
from models import User, DetectionHistory, ChatHistory, db
from utils.response import success, bad_request, not_found, error
from middleware.auth_middleware import admin_required


def _get_user_with_counts(user):
    """获取用户信息并附带检测数和对话数"""
    data = user.to_dict()
    data['is_active'] = user.is_active
    data['detection_count'] = user.detection_histories.count()
    data['chat_count'] = user.chat_histories.count()
    return data


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    """获取用户列表（分页、筛选）

    Query Params:
        page: 页码，默认 1
        page_size: 每页数量，默认 20
        role: 角色筛选 user/admin
        status: 状态筛选 active/inactive
        keyword: 用户名/邮箱搜索
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    role_filter = request.args.get('role', '').strip()
    status_filter = request.args.get('status', '').strip()
    keyword = request.args.get('keyword', '').strip()

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = User.query

    if role_filter and role_filter in ('user', 'admin'):
        query = query.filter(User.role == role_filter)

    if status_filter == 'active':
        query = query.filter(User.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(User.is_active == False)

    if keyword:
        # 使用 func.concat 避免 SQL 注入
        query = query.filter(
            (User.username.like(func.concat('%', keyword, '%'))) |
            (User.email.like(func.concat('%', keyword, '%')))
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [_get_user_with_counts(u) for u in users],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@admin_bp.route('/users/stats', methods=['GET'])
@admin_required
def get_user_stats(current_user):
    """获取用户统计数据"""
    total = User.query.count()
    active = User.query.filter_by(is_active=True).count()

    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    new_today = User.query.filter(User.created_at >= today_start).count()

    return success(data={
        'total': total,
        'active': active,
        'new_today': new_today
    })


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_detail(current_user, user_id):
    """获取用户详情"""
    user = User.query.get(user_id)
    if not user:
        return not_found('用户不存在')

    return success(data=_get_user_with_counts(user))


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(current_user, user_id):
    """启用/禁用用户

    Body: { is_active: bool }
    """
    user = User.query.get(user_id)
    if not user:
        return not_found('用户不存在')

    if user.id == current_user.id:
        return bad_request('不能修改自己的状态')

    data = request.get_json() or {}
    is_active = data.get('is_active')

    if is_active is None:
        return bad_request('is_active 参数不能为空')

    user.is_active = bool(is_active)
    db.session.commit()

    message = '用户已启用' if user.is_active else '用户已禁用'
    return success(message=message)


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(current_user, user_id):
    """修改用户角色

    Body: { role: 'user'|'admin' }
    """
    user = User.query.get(user_id)
    if not user:
        return not_found('用户不存在')

    data = request.get_json() or {}
    role = data.get('role', '').strip()

    if role not in ('user', 'admin'):
        return bad_request('角色值无效，只能是 user 或 admin')

    user.role = role
    db.session.commit()

    return success(message='角色已更新')


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    """删除用户（同时删除其检测历史、对话历史）"""
    user = User.query.get(user_id)
    if not user:
        return not_found('用户不存在')

    if user.id == current_user.id:
        return bad_request('不能删除自己')

    try:
        # 删除关联数据（使用事务保护）
        deleted_detections = DetectionHistory.query.filter_by(user_id=user_id).delete()
        deleted_chats = ChatHistory.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()

        return success(message='用户已删除', data={
            'deleted_detections': deleted_detections,
            'deleted_chats': deleted_chats
        })
    except Exception as e:
        db.session.rollback()
        return error(message=f'删除失败: {str(e)}')
