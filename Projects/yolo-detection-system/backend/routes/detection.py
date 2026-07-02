import os
from flask import Blueprint, request, current_app
from models import DetectionHistory, db
from utils.response import success, bad_request
from utils.file_utils import allowed_file, save_uploaded_file, get_file_size, get_relative_url
from middleware.auth_middleware import login_required
from services.yolo_service import yolo_service

detection_bp = Blueprint('detection', __name__, url_prefix='/api/detect')


@detection_bp.route('/image', methods=['POST'])
@login_required
def detect_image(current_user):
    """图片目标检测"""
    if 'file' not in request.files:
        return bad_request('请上传图片文件')

    file = request.files['file']
    if file.filename == '':
        return bad_request('文件名为空')

    # 检查文件类型
    allowed_extensions = current_app.config['ALLOWED_IMAGE_EXTENSIONS']
    if not allowed_file(file.filename, allowed_extensions):
        return bad_request(f'不支持的图片格式，支持: {", ".join(allowed_extensions)}')

    save_history = request.form.get('save_history', 'true').lower() == 'true'

    # 保存上传文件
    upload_dir = current_app.config['UPLOAD_FOLDER']
    result_dir = current_app.config['RESULT_FOLDER']
    save_path, new_filename, original_name = save_uploaded_file(file, upload_dir)

    # 执行检测
    detect_result = yolo_service.detect_image(save_path, result_dir, save_result=True)

    # 构建结果路径 URL
    result_image_url = None
    if detect_result.get('result_path'):
        static_dir = os.path.join(current_app.root_path, 'static')
        result_image_url = get_relative_url(detect_result['result_path'], static_dir)

    original_image_url = get_relative_url(save_path, os.path.join(current_app.root_path, 'static'))

    # 保存历史记录
    history_id = None
    if save_history:
        file_size = get_file_size(save_path)
        history = DetectionHistory(
            user_id=current_user.id,
            type='image',
            original_filename=original_name,
            original_path=original_image_url,
            result_path=result_image_url,
            detection_count=detect_result['total_count'],
            file_size=file_size,
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
        history_id = history.id

    return success(data={
        'id': history_id,
        'result_image': result_image_url,
        'original_image': original_image_url,
        'detections': detect_result['detections'],
        'total_count': detect_result['total_count'],
        'class_summary': detect_result['class_summary'],
        'processing_time': detect_result['processing_time'],
        'model_version': detect_result['model_version']
    }, message='检测完成')
