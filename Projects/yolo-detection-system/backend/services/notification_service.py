"""站内通知服务

集中封装通知的创建、查询与已读操作，供路由层调用。
"""
from typing import Optional

from models import Notification, db

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20


def create_notification(
    user_id: int,
    notify_type: str,
    title: str,
    content: Optional[str] = None,
    related_type: Optional[str] = None,
    related_id: Optional[int] = None
) -> Notification:
    """创建一条通知（不提交事务，由调用方决定提交时机）

    Args:
        user_id: 接收人用户 ID
        notify_type: 通知类型，见 Notification.TYPE_*
        title: 通知标题
        content: 通知正文
        related_type: 关联业务类型，如 detection / knowledge
        related_id: 关联业务主键

    Returns:
        Notification: 新建的通知对象
    """
    notification = Notification(
        user_id=user_id,
        type=notify_type,
        title=title,
        content=content,
        related_type=related_type,
        related_id=related_id
    )
    db.session.add(notification)
    return notification


def notify_detection_completed(user_id: int, history_id: int, filename: str,
                               detection_count: int) -> Notification:
    """检测完成后写入通知

    Args:
        user_id: 用户 ID
        history_id: 检测历史 ID
        filename: 原始文件名
        detection_count: 检出目标数量

    Returns:
        Notification: 新建的通知对象
    """
    return create_notification(
        user_id=user_id,
        notify_type=Notification.TYPE_DETECTION_COMPLETED,
        title='图片检测完成',
        content=f'《{filename}》检测完成，共识别到 {detection_count} 个目标。',
        related_type='detection',
        related_id=history_id
    )


def notify_knowledge_review(user_id: int, kb_id: int, title: str, approved: bool) -> Notification:
    """知识审核结果通知

    Args:
        user_id: 知识上传者用户 ID
        kb_id: 知识 ID
        title: 知识标题
        approved: 是否审核通过

    Returns:
        Notification: 新建的通知对象
    """
    notify_type = Notification.TYPE_KNOWLEDGE_APPROVED if approved \
        else Notification.TYPE_KNOWLEDGE_REJECTED
    result_text = '已通过审核' if approved else '未通过审核'
    return create_notification(
        user_id=user_id,
        notify_type=notify_type,
        title=f'知识投稿{result_text}',
        content=f'您投稿的知识《{title}》{result_text}。',
        related_type='knowledge',
        related_id=kb_id
    )


def list_for_user(user_id: int, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
                  is_read: Optional[bool] = None, notify_type: Optional[str] = None) -> dict:
    """分页查询用户通知

    Args:
        user_id: 用户 ID
        page: 页码，从 1 开始
        page_size: 每页条数，1..100
        is_read: 是否已读筛选，None 表示不筛选
        notify_type: 通知类型筛选，None 表示不筛选

    Returns:
        dict: {list, total, page, page_size, unread_count}
    """
    query = Notification.query.filter(Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    if notify_type:
        query = query.filter(Notification.type == notify_type)

    total = query.count()
    items = query.order_by(Notification.created_at.desc(), Notification.id.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return {
        'list': [item.to_dict() for item in items],
        'total': total,
        'page': page,
        'page_size': page_size,
        'unread_count': unread_count(user_id)
    }


def unread_count(user_id: int) -> int:
    """统计用户未读通知数

    Args:
        user_id: 用户 ID

    Returns:
        int: 未读条数
    """
    return Notification.query.filter(
        Notification.user_id == user_id,
        Notification.is_read == False  # noqa: E712 - 需与 SQLAlchemy 布尔列比较
    ).count()


def mark_all_read(user_id: int) -> int:
    """将用户全部未读通知标记为已读

    Args:
        user_id: 用户 ID

    Returns:
        int: 本次更新条数
    """
    updated = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.is_read == False  # noqa: E712 - 需与 SQLAlchemy 布尔列比较
    ).update({Notification.is_read: True}, synchronize_session=False)
    db.session.commit()
    return updated