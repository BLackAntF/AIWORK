from flask import request
from routes.admin import admin_bp
from models import DiseaseProfile, db
from utils.response import success, bad_request, not_found
from middleware.auth_middleware import admin_required
from utils.audit import log_admin_action

# 管理端可写字段（含防治方案结构化字段）
EDITABLE_FIELDS = ('disease_name', 'causes', 'symptoms', 'occurrence', 'prevention',
                   'treatment', 'pesticides', 'dosage', 'safety_interval',
                   'biological_control', 'is_active')


@admin_bp.route('/disease-profiles/<int:profile_id>', methods=['PUT'])
@admin_required
def update_disease_profile(current_user, profile_id):
    """更新病害档案（含用药剂量 / 安全间隔期 / 生物防治）

    Args:
        profile_id: 档案主键
    Body:
        任意可写字段；is_active 按布尔值处理
    """
    profile = DiseaseProfile.query.get(profile_id)
    if not profile:
        return not_found('病害档案不存在')

    data = request.get_json() or {}
    fields = [field for field in EDITABLE_FIELDS if field in data]
    if not fields:
        return bad_request('未提供可更新字段')

    for field in fields:
        value = bool(data[field]) if field == 'is_active' else data[field]
        setattr(profile, field, value)
    db.session.commit()

    log_admin_action(
        user_id=current_user.id,
        username=current_user.username,
        action='update_disease_profile',
        target_type='disease_profile',
        target_id=profile.id,
        detail=f"更新病害档案: {profile.disease_name} ({', '.join(fields)})"
    )

    return success(data=profile.to_dict(), message='病害档案已更新')
