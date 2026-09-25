from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError
from models import User
from utils.response import unauthorized, forbidden


def _load_user(user_id):
    """按 JWT 身份加载用户，身份非法时返回 None

    Args:
        user_id: JWT 中的身份标识

    Returns:
        User | None: 匹配的用户，身份非法或不存在时为 None
    """
    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None


def login_required(fn):
    """登录认证装饰器

    验证 JWT token 并注入 current_user 到 kwargs 中。
    仅捕获 JWT 校验相关异常，路由内部异常交由全局错误处理，
    避免内部异常被误判为 401。
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except (JWTExtendedException, PyJWTError):
            # PyJWTError 覆盖 token 格式错误/签名错误/已过期等情况，
            # 统一按项目响应约定返回 code=401（HTTP 200）
            return unauthorized('Token无效或已过期')

        if not user_id:
            return unauthorized('请先登录')

        user = _load_user(user_id)
        if not user or not user.is_active:
            return unauthorized('用户不存在或已禁用')

        kwargs['current_user'] = user
        return fn(*args, **kwargs)

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
