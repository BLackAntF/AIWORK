from flask import jsonify


def success(data=None, message='success'):
    """成功响应

    Args:
        data: 返回数据
        message: 消息描述

    Returns:
        tuple: (json响应, 状态码)
    """
    return jsonify({
        'code': 0,
        'message': message,
        'data': data
    }), 200


def error(code=500, message='error', data=None):
    """错误响应

    Args:
        code: 错误码
        message: 错误消息
        data: 附加数据

    Returns:
        tuple: (json响应, 状态码)
    """
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), 200


def bad_request(message='请求参数错误', data=None):
    """400 错误响应"""
    return error(code=400, message=message, data=data)


def unauthorized(message='未认证或Token无效'):
    """401 错误响应"""
    return error(code=401, message=message)


def forbidden(message='无权限访问'):
    """403 错误响应"""
    return error(code=403, message=message)


def not_found(message='资源不存在'):
    """404 错误响应"""
    return error(code=404, message=message)


def server_error(message='服务器内部错误'):
    """500 错误响应"""
    return error(code=500, message=message)
