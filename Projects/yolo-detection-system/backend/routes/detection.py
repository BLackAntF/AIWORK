import os
from typing import Optional

from flask import Blueprint, request, current_app
from models import DetectionHistory, db
from utils.response import success, bad_request, server_error
from utils.file_utils import allowed_file, save_uploaded_file, get_file_size, get_relative_url
from middleware.auth_middleware import login_required
from services.yolo_service import yolo_service
from services.disease_profile_service import disease_profile_service
from services import notification_service

detection_bp = Blueprint('detection', __name__, url_prefix='/api/detect')


def _validate_image_file(filename: str) -> Optional[str]:
    """校验图片文件名

    Args:
        filename: 原始文件名

    Returns:
        str | None: 错误消息，通过校验时为 None
    """
    allowed_extensions = current_app.config['ALLOWED_IMAGE_EXTENSIONS']
    if not filename:
        return '文件名为空'
    if not allowed_file(filename, allowed_extensions):
        return f'不支持的图片格式，支持: {", ".join(allowed_extensions)}'
    return None


def _should_save_history() -> bool:
    """读取表单中的 save_history 开关

    Returns:
        bool: 是否保存历史记录，默认 True
    """
    return request.form.get('save_history', 'true').lower() == 'true'


def _save_history(user_id: int, original_name: str, original_image_url: str,
                  result_image_url: Optional[str], save_path: str,
                  detect_result: dict) -> int:
    """写入检测历史并发出站内通知

    Args:
        user_id: 用户 ID
        original_name: 原始文件名
        original_image_url: 原图 URL
        result_image_url: 结果图 URL
        save_path: 上传文件保存路径
        detect_result: yolo_service.detect_image 的返回值

    Returns:
        int: 历史记录 ID
    """
    history = DetectionHistory(
        user_id=user_id,
        type='image',
        original_filename=original_name,
        original_path=original_image_url,
        result_path=result_image_url,
        detection_count=detect_result['total_count'],
        file_size=get_file_size(save_path),
        processing_time=detect_result['processing_time'],
        model_version=detect_result['model_version']
    )
    history.set_detection_result({
        'detections': detect_result['detections'],
        'total_count': detect_result['total_count'],
        'class_summary': detect_result['class_summary']
    })
    db.session.add(history)
    db.session.commit()

    notification_service.notify_detection_completed(
        user_id=user_id,
        history_id=history.id,
        filename=original_name,
        detection_count=detect_result['total_count']
    )
    db.session.commit()
    return history.id


def _detect_one(file, user_id: int, save_history: bool) -> dict:
    """处理单张图片检测，单图失败不影响整体

    Args:
        file: Flask 上传文件对象（调用前需已通过格式校验）
        user_id: 用户 ID
        save_history: 是否保存历史记录

    Returns:
        dict: 单图检测结果，失败时含 success=False 与 error
    """
    original_name = file.filename
    try:
        upload_dir = current_app.config['UPLOAD_FOLDER']
        result_dir = current_app.config['RESULT_FOLDER']
        static_dir = os.path.join(current_app.root_path, 'static')

        save_path, _, original_name = save_uploaded_file(file, upload_dir)
        detect_result = yolo_service.detect_image(save_path, result_dir, save_result=True)

        result_image_url = get_relative_url(detect_result['result_path'], static_dir) \
            if detect_result.get('result_path') else None
        original_image_url = get_relative_url(save_path, static_dir)

        history_id = _save_history(user_id, original_name, original_image_url,
                                  result_image_url, save_path, detect_result) \
            if save_history else None

        for det in detect_result['detections']:
            class_id = det.get('class_id')
            det['disease_profile'] = disease_profile_service.get_profile_for_llm(class_id) \
                if class_id is not None else None

        return {
            'original_filename': original_name,
            'id': history_id,
            'result_image': result_image_url,
            'original_image': original_image_url,
            'detections': detect_result['detections'],
            'total_count': detect_result['total_count'],
            'class_summary': detect_result['class_summary'],
            'processing_time': detect_result['processing_time'],
            'model_version': detect_result['model_version'],
            'success': True,
            'error': None
        }
    except Exception as exc:  # noqa: BLE001 - 单图失败需降级为结果项而非中断批量
        current_app.logger.exception('图片检测失败: %s', original_name)
        db.session.rollback()
        return {
            'original_filename': original_name,
            'success': False,
            'error': str(exc)
        }


@detection_bp.route('/image', methods=['POST'])
@login_required
def detect_image(current_user):
    """图片目标检测"""
    if 'file' not in request.files:
        return bad_request('请上传图片文件')

    file = request.files['file']
    error_message = _validate_image_file(file.filename)
    if error_message:
        return bad_request(error_message)

    result = _detect_one(file, current_user.id, _should_save_history())
    if not result['success']:
        return server_error(result['error'])

    return success(data=result, message='检测完成')


@detection_bp.route('/batch', methods=['POST'])
@login_required
def detect_batch(current_user):
    """批量图片目标检测（部分失败不整体报错）

    Form:
        files: 多张图片（字段名 files，1..MAX_BATCH_IMAGES）
        save_history: 是否保存历史记录，默认 true
    """
    files = [f for f in request.files.getlist('files') if f and f.filename]
    if not files:
        return bad_request('请上传图片文件')

    max_batch = current_app.config['MAX_BATCH_IMAGES']
    if len(files) > max_batch:
        return bad_request(f'单次最多上传 {max_batch} 张图片')

    save_history = _should_save_history()
    results = []
    for file in files:
        error_message = _validate_image_file(file.filename)
        if error_message:
            results.append({
                'original_filename': file.filename,
                'success': False,
                'error': error_message
            })
            continue
        results.append(_detect_one(file, current_user.id, save_history))

    success_count = sum(1 for item in results if item['success'])
    return success(data={
        'list': results,
        'total': len(results),
        'success_count': success_count,
        'failed_count': len(results) - success_count
    }, message='批量检测完成')