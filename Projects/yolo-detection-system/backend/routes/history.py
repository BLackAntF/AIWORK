from flask import Blueprint, request
from sqlalchemy import func
from models import DetectionHistory, db
from utils.response import success, bad_request, not_found
from middleware.auth_middleware import login_required

history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('', methods=['GET'])
@login_required
def get_history_list(current_user):
    """获取检测历史列表"""
    type_ = request.args.get('type', '').strip() or None
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', '').strip() or None

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10

    query = DetectionHistory.query.filter_by(user_id=current_user.id)

    if type_ and type_ in ('image', 'video'):
        query = query.filter_by(type=type_)

    if keyword:
        # 使用 func.concat 避免 SQL 注入
        query = query.filter(DetectionHistory.original_filename.like(func.concat('%', keyword, '%')))

    total = query.count()
    items = query.order_by(DetectionHistory.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [item.to_dict(include_detail=False) for item in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@history_bp.route('/<int:history_id>', methods=['GET'])
@login_required
def get_history_detail(current_user, history_id):
    """获取单条历史详情"""
    item = DetectionHistory.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first()

    if not item:
        return not_found('记录不存在')

    return success(data=item.to_dict(include_detail=True))


@history_bp.route('/<int:history_id>', methods=['DELETE'])
@login_required
def delete_history(current_user, history_id):
    """删除单条历史记录"""
    item = DetectionHistory.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first()

    if not item:
        return not_found('记录不存在')

    db.session.delete(item)
    db.session.commit()

    return success(message='删除成功')


@history_bp.route('', methods=['DELETE'])
@login_required
def batch_delete_history(current_user):
    """批量删除历史记录"""
    data = request.get_json() or {}
    ids = data.get('ids', [])

    if not ids or not isinstance(ids, list):
        return bad_request('请提供要删除的记录ID列表')

    deleted = DetectionHistory.query.filter(
        DetectionHistory.id.in_(ids),
        DetectionHistory.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.session.commit()

    return success(message='批量删除成功', data={'deleted_count': deleted})
