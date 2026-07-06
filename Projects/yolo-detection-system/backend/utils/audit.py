from flask import request
from models import AdminLog, db


def log_admin_action(user_id, username, action, target_type=None, target_id=None, detail=None):
    log = AdminLog(
        user_id=user_id,
        username=username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=_get_client_ip(),
        user_agent=_get_user_agent()
    )
    db.session.add(log)
    db.session.commit()
    return log


def _get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'


def _get_user_agent():
    return request.headers.get('User-Agent', '')[:255]


def log_user_action(user_id, username, action, target_user_id, detail=None):
    return log_admin_action(
        user_id=user_id,
        username=username,
        action=action,
        target_type='user',
        target_id=target_user_id,
        detail=detail
    )


def log_knowledge_action(user_id, username, action, knowledge_id, detail=None):
    return log_admin_action(
        user_id=user_id,
        username=username,
        action=action,
        target_type='knowledge',
        target_id=knowledge_id,
        detail=detail
    )


def log_category_action(user_id, username, action, category_id, detail=None):
    return log_admin_action(
        user_id=user_id,
        username=username,
        action=action,
        target_type='category',
        target_id=category_id,
        detail=detail
    )


def log_config_action(user_id, username, config_key, detail=None):
    return log_admin_action(
        user_id=user_id,
        username=username,
        action='update_config',
        target_type='config',
        target_id=None,
        detail=f"{config_key}: {detail}"
    )


def log_model_action(user_id, username, action, model_id, detail=None):
    return log_admin_action(
        user_id=user_id,
        username=username,
        action=action,
        target_type='model',
        target_id=model_id,
        detail=detail
    )


def log_detection_action(user_id, username, action, detection_id, detail=None):
    return log_admin_action(
        user_id=user_id,
        username=username,
        action=action,
        target_type='detection',
        target_id=detection_id,
        detail=detail
    )
