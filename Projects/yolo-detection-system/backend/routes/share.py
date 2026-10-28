from flask import Blueprint, jsonify
from models import DiseaseProfile, ShareLink, iso_utc
from utils.response import success

share_bp = Blueprint('share', __name__, url_prefix='/api/share')

INVALID_TOKEN_MESSAGE = '分享链接不存在或已被删除'
EXPIRED_TOKEN_MESSAGE = '分享链接已过期'


def _json_error(status: int, message: str) -> tuple:
    """返回带真实 HTTP 状态码的错误响应

    Args:
        status: HTTP 状态码
        message: 中文提示

    Returns:
        tuple: (json 响应, 状态码)
    """
    return jsonify({'code': status, 'message': message, 'data': None}), status


def _build_shared_payload(link: ShareLink) -> dict:
    """组装只读检测结果（不含用户名、邮箱等隐私字段）

    Args:
        link: 分享链接记录

    Returns:
        dict: 历史基本信息 + 检测明细 + 关联病害档案
    """
    item = link.history
    result = item.get_detection_result() or {}
    detections = result.get('detections') or []

    profiles = {}
    for det in detections:
        class_id = det.get('class_id')
        if class_id is None or class_id in profiles:
            continue
        profile = DiseaseProfile.query.filter_by(class_id=class_id, is_active=True).first()
        profiles[class_id] = profile.to_dict() if profile else None

    for det in detections:
        det['disease_profile'] = profiles.get(det.get('class_id'))

    return {
        'history': {
            'id': item.id,
            'original_filename': item.original_filename,
            'created_at': iso_utc(item.created_at),
            'model_version': item.model_version,
            'detection_count': item.detection_count,
            'max_confidence': item.max_confidence,
            'class_names': item.class_names,
            'original_image': item.original_path,
            'result_image': item.result_path
        },
        'detections': detections,
        'expires_at': iso_utc(link.expires_at)
    }


@share_bp.route('/<string:token>', methods=['GET'])
def get_shared_detection(token: str):
    """公开访问分享的检测结果（无需登录、只读）

    Args:
        token: 分享令牌
    """
    link = ShareLink.query.filter_by(token=token).first()
    if not link:
        return _json_error(404, INVALID_TOKEN_MESSAGE)
    if link.is_expired():
        return _json_error(410, EXPIRED_TOKEN_MESSAGE)
    if not link.history:
        return _json_error(404, INVALID_TOKEN_MESSAGE)

    return success(data=_build_shared_payload(link))
