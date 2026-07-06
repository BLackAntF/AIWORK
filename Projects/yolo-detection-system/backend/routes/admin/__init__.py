from flask import Blueprint, request
from sqlalchemy import func
from datetime import datetime, timedelta
from models import AdminLog, db
from utils.response import success
from middleware.auth_middleware import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

from . import users, knowledge, detections, stats, config


@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs(current_user):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    page_size = min(page_size, 100)

    action = request.args.get('action', '').strip()
    target_type = request.args.get('target_type', '').strip()
    keyword = request.args.get('keyword', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    query = AdminLog.query

    if action:
        query = query.filter(AdminLog.action == action)
    if target_type:
        query = query.filter(AdminLog.target_type == target_type)
    if keyword:
        query = query.filter(
            db.or_(
                AdminLog.username.like(f'%{keyword}%'),
                AdminLog.detail.like(f'%{keyword}%')
            )
        )
    if start_date:
        query = query.filter(AdminLog.created_at >= start_date)
    if end_date:
        query = query.filter(AdminLog.created_at <= end_date)

    query = query.order_by(AdminLog.created_at.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    logs = [log.to_dict() for log in pagination.items]

    return success(data={
        'logs': logs,
        'total': pagination.total,
        'page': pagination.page,
        'page_size': pagination.per_page,
        'pages': pagination.pages
    })


@admin_bp.route('/logs/actions', methods=['GET'])
@admin_required
def get_action_types(current_user):
    actions = [
        {'value': 'login', 'label': '登录'},
        {'value': 'logout', 'label': '登出'},
        {'value': 'create_user', 'label': '创建用户'},
        {'value': 'update_user', 'label': '更新用户'},
        {'value': 'delete_user', 'label': '删除用户'},
        {'value': 'toggle_user_status', 'label': '启用/禁用用户'},
        {'value': 'change_user_role', 'label': '修改用户角色'},
        {'value': 'create_knowledge', 'label': '创建知识'},
        {'value': 'update_knowledge', 'label': '更新知识'},
        {'value': 'delete_knowledge', 'label': '删除知识'},
        {'value': 'batch_delete_knowledge', 'label': '批量删除知识'},
        {'value': 'create_category', 'label': '创建分类'},
        {'value': 'update_category', 'label': '更新分类'},
        {'value': 'delete_category', 'label': '删除分类'},
        {'value': 'update_config', 'label': '更新配置'},
        {'value': 'switch_model', 'label': '切换模型'},
        {'value': 'upload_model', 'label': '上传模型'},
        {'value': 'delete_detection', 'label': '删除检测记录'},
        {'value': 'batch_delete_detections', 'label': '批量删除检测记录'},
    ]
    return success(data={'actions': actions})


@admin_bp.route('/logs/stats', methods=['GET'])
@admin_required
def get_log_stats(current_user):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_logs = AdminLog.query.count()

    today_logs = AdminLog.query.filter(
        func.date(AdminLog.created_at) == today
    ).count()

    week_logs = AdminLog.query.filter(
        AdminLog.created_at >= week_ago
    ).count()

    month_logs = AdminLog.query.filter(
        AdminLog.created_at >= month_ago
    ).count()

    action_stats = db.session.query(
        AdminLog.action,
        func.count(AdminLog.id).label('count')
    ).group_by(AdminLog.action).order_by(func.count(AdminLog.id).desc()).limit(10).all()

    action_distribution = [{'action': a, 'count': c} for a, c in action_stats]

    return success(data={
        'total_logs': total_logs,
        'today_logs': today_logs,
        'week_logs': week_logs,
        'month_logs': month_logs,
        'action_distribution': action_distribution
    })
