import os
from datetime import datetime
from flask import request, current_app
from routes.admin import admin_bp
from models import SystemConfig, ModelInfo, db
from utils.response import success, bad_request, not_found, error
from middleware.auth_middleware import admin_required


@admin_bp.route('/config', methods=['GET'])
@admin_required
def get_configs(current_user):
    """获取配置列表"""
    configs = SystemConfig.query.all()
    return success(data=[c.to_dict() for c in configs])


@admin_bp.route('/config/<config_key>', methods=['PUT'])
@admin_required
def update_config(current_user, config_key):
    """更新配置

    Body: { value: string }
    """
    config = SystemConfig.query.filter_by(config_key=config_key).first()
    if not config:
        return not_found('配置项不存在')

    data = request.get_json() or {}
    value = data.get('value')

    if value is None:
        return bad_request('value 参数不能为空')

    config.config_value = str(value)
    config.updated_at = datetime.utcnow()
    db.session.commit()

    return success(data=config.to_dict(), message='配置已更新')


@admin_bp.route('/models', methods=['GET'])
@admin_required
def get_models(current_user):
    """获取模型列表"""
    models = ModelInfo.query.order_by(ModelInfo.created_at.desc()).all()
    return success(data=[m.to_dict() for m in models])


@admin_bp.route('/models', methods=['POST'])
@admin_required
def upload_model(current_user):
    """上传模型（文件上传 + name）"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip() or None
    file = request.files.get('file')

    if not name:
        return bad_request('模型名称不能为空')
    if not file:
        return bad_request('请上传模型文件')

    try:
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'models')
        os.makedirs(upload_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = ''.join(c for c in file.filename if c.isalnum() or c in ('.', '_', '-'))
        filename = f"{timestamp}_{safe_name}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        version = f"v{ModelInfo.query.count() + 1}"

        model = ModelInfo(
            name=name,
            path=filepath,
            version=version,
            description=description,
            is_active=False
        )
        db.session.add(model)
        db.session.commit()

        return success(data=model.to_dict(), message='模型上传成功')

    except Exception as e:
        db.session.rollback()
        return error(message=f'上传失败: {str(e)}')


@admin_bp.route('/models/active', methods=['PUT'])
@admin_required
def set_active_model(current_user):
    """切换激活模型

    Body: { model_id: int }
    """
    data = request.get_json() or {}
    model_id = data.get('model_id')

    if not model_id:
        return bad_request('model_id 参数不能为空')

    model = ModelInfo.query.get(model_id)
    if not model:
        return not_found('模型不存在')

    # 先将所有模型设为非激活
    ModelInfo.query.update({ModelInfo.is_active: False})
    db.session.flush()

    # 激活选中的模型
    model.is_active = True
    db.session.commit()

    return success(message='模型已激活')
