from flask import Blueprint, request
from models import SamplePool, DetectionHistory, db
from utils.response import success, bad_request, not_found
from middleware.auth_middleware import login_required

sample_pool_bp = Blueprint('sample_pool', __name__, url_prefix='/api/sample-pool')


@sample_pool_bp.route('', methods=['POST'])
@login_required
def submit_sample(current_user):
    """用户对检测结果提交纠错反馈，进入增量样本池待审核

    Body:
        history_id: int 检测记录 ID（须为本人的）
        mark_type: correct / misclassified / missed / uncertain
        corrected_class: str 类别纠正（mark_type=misclassified 时必填）
        note: str 补充说明（可选）
    """
    data = request.get_json() or {}
    history_id = data.get('history_id')
    mark_type = data.get('mark_type', '').strip()
    corrected_class = data.get('corrected_class', '').strip()
    note = data.get('note', '').strip()

    if not history_id:
        return bad_request('history_id 不能为空')
    if mark_type not in SamplePool.MARK_TYPES:
        return bad_request(f'mark_type 必须为 {"/".join(SamplePool.MARK_TYPES)}')
    if mark_type == SamplePool.MARK_MISCLASSIFIED and not corrected_class:
        return bad_request('类别纠错时 corrected_class 必填')

    item = DetectionHistory.query.filter_by(
        id=history_id, user_id=current_user.id
    ).first()
    if not item:
        return not_found('检测记录不存在')

    existed = SamplePool.query.filter(
        SamplePool.user_id == current_user.id,
        SamplePool.history_id == history_id,
        SamplePool.status != SamplePool.STATUS_REJECTED
    ).first()
    if existed:
        if not existed.auto_created:
            return bad_request('该记录已提交过反馈，请等待审核')
        # 用户手动反馈覆盖系统自动收录的记录，避免重复条目
        existed.mark_type = mark_type
        existed.corrected_class = corrected_class or None
        existed.note = note or None
        existed.auto_created = False
        db.session.commit()
        return success(data=existed.to_dict(), message='反馈已提交，感谢协助改进模型')

    predicted_class = ''
    if item.class_names:
        predicted_class = item.class_names.split(',')[0].strip()

    sample = SamplePool(
        user_id=current_user.id,
        history_id=history_id,
        image_path=item.original_path or '',
        predicted_class=predicted_class or None,
        predicted_confidence=item.max_confidence,
        mark_type=mark_type,
        corrected_class=corrected_class or None,
        note=note or None
    )
    db.session.add(sample)
    db.session.commit()

    return success(data=sample.to_dict(), message='反馈已提交，感谢协助改进模型')


@sample_pool_bp.route('', methods=['GET'])
@login_required
def list_my_samples(current_user):
    """我的反馈提交记录"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)

    pagination = SamplePool.query.filter_by(user_id=current_user.id) \
        .order_by(SamplePool.created_at.desc()) \
        .paginate(page=page, per_page=page_size, error_out=False)

    return success(data={
        'list': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size
    })
