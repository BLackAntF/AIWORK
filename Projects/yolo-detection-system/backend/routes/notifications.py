"""站内通知接口

提供通知列表、未读数、标记已读与删除能力，全部要求登录，
并按 user_id 做越权保护。
"""
from typing import Optional

from flask import Blueprint, request

from models import Notification, db
from services import notification_service
from utils.response import success, bad_request, not_found
from middleware.auth_middleware import login_required

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
VALID_TYPES = (
    Notification.TYPE_DETECTION_COMPLETED,
    Notification.TYPE_KNOWLEDGE_APPROVED,
    Notification.TYPE_KNOWLEDGE_REJECTED,
    Notification.TYPE_SYSTEM,
)


def _parse_pagination() -> tuple:
    """解析 page / page_size 查询参数

    Returns:
        tuple: (page, page_size)
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        return 1, DEFAULT_PAGE_SIZE

    if page < 1:
        page = 1
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        page_size = DEFAULT_PAGE_SIZE
    return page, page_size


def _parse_is_read() -> Optional[bool]:
    """解析 is_read 查询参数

    Returns:
        bool | None: True/False 为筛选条件，None 表示不筛选
    """
    raw = request.args.get('is_read', '').strip().lower()
    if raw == 'true':
        return True
    if raw == 'false':
        return False
    return None


@notifications_bp.route('', methods=['GET'])
@login_required
def list_notifications(current_user) -> tuple:
    """获取当前用户的通知列表

    Query:
        page: 页码，默认 1
        page_size: 每页条数，1..100，默认 20
        is_read: 已读状态筛选，true / false
        type: 通知类型筛选
    """
    page, page_size = _parse_pagination()
    notify_type = request.args.get('type', '').strip() or None
    if notify_type and notify_type not in VALID_TYPES:
        return bad_request('无效的通知类型')

    data = notification_service.list_for_user(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        is_read=_parse_is_read(),
        notify_type=notify_type
    )
    return success(data=data)


@notifications_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count(current_user) -> tuple:
    """获取当前用户未读通知数"""
    return success(data={'unread_count': notification_service.unread_count(current_user.id)})


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(current_user, notification_id: int) -> tuple:
    """将指定通知标记为已读（仅限本人的通知）

    Args:
        notification_id: 通知 ID
    """
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    if not notification:
        return not_found('通知不存在')

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    return success(data=notification.to_dict(), message='已标记为已读')


@notifications_bp.route('/read-all', methods=['PUT'])
@login_required
def mark_all_notifications_read(current_user) -> tuple:
    """将当前用户全部通知标记为已读"""
    updated = notification_service.mark_all_read(current_user.id)
    return success(data={'updated_count': updated}, message='全部标记为已读')


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(current_user, notification_id: int) -> tuple:
    """删除指定通知（仅限本人的通知）

    Args:
        notification_id: 通知 ID
    """
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    if not notification:
        return not_found('通知不存在')

    db.session.delete(notification)
    db.session.commit()
    return success(message='通知已删除')