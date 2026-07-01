import re
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from models import User, db
from utils.response import success, bad_request, unauthorized
from middleware.auth_middleware import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 邮箱格式正则
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip() or None

    # 参数验证
    if not username or len(username) < 3 or len(username) > 50:
        return bad_request('用户名长度应为3-50个字符')
    if not password or len(password) < 6 or len(password) > 50:
        return bad_request('密码长度应为6-50个字符')
    if email and len(email) > 100:
        return bad_request('邮箱长度不能超过100个字符')
    # 邮箱格式校验
    if email and not re.match(EMAIL_REGEX, email):
        return bad_request('邮箱格式不正确')

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return bad_request('用户名已存在')

    # 检查邮箱是否已存在
    if email and User.query.filter_by(email=email).first():
        return bad_request('邮箱已被注册')

    # 创建用户
    user = User(username=username, email=email, role='user')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return success(data={'id': user.id, 'username': user.username}, message='注册成功')


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return bad_request('用户名和密码不能为空')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return unauthorized('用户名或密码错误')

    if not user.is_active:
        return unauthorized('账号已被禁用')

    # 生成 token
    access_token = create_access_token(identity=str(user.id))

    return success(data={
        'access_token': access_token,
        'user': user.to_dict()
    }, message='登录成功')


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user(current_user):
    """获取当前登录用户信息"""
    return success(data=current_user.to_dict())


@auth_bp.route('/password', methods=['PUT'])
@login_required
def change_password(current_user):
    """修改密码"""
    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return bad_request('原密码和新密码不能为空')

    if len(new_password) < 6 or len(new_password) > 50:
        return bad_request('新密码长度应为6-50个字符')

    if not current_user.check_password(old_password):
        return bad_request('原密码错误')

    current_user.set_password(new_password)
    db.session.commit()

    return success(message='密码修改成功')
