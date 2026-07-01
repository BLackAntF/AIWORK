from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User
from utils.response import unauthorized, forbidden


def login_required(fn):
    """登录认证装饰器

    验证 JWT token 并注入 current_user 到 kwargs 中
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if not user_id:
                return unauthorized('请先登录')

            user = User.query.get(int(user_id))
            if not user or not user.is_active:
                return unauthorized('用户不存在或已禁用')

            kwargs['current_user'] = user
            return fn(*args, **kwargs)
        except Exception:
            return unauthorized('Token无效或已过期')

    return wrapper


def admin_required(fn):
    """管理员权限装饰器

    需要先通过 login_required 验证，再检查角色是否为 admin
    """
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        user = kwargs.get('current_user')
        if not user or user.role != 'admin':
            return forbidden('需要管理员权限')
        return fn(*args, **kwargs)

    return wrapper
