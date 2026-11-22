from flask import Blueprint, request, current_app
from models import SamplePool, DetectionHistory, db
from utils.response import success, bad_request, not_found, error
from utils.params import parse_pagination
from middleware.auth_middleware import login_required, check_rate_limit

sample_pool_bp = Blueprint('sample_pool', __name__, url_prefix='/api/sample-pool')

MAX_CORRECTED_CLASS_LENGTH = 100
MAX_NOTE_LENGTH = 200


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
    limit = current_app.config['SAMPLE_FEEDBACK_RATE_LIMIT_PER_MINUTE']
    if not check_rate_limit(f'sample-feedback:{current_user.id}', limit):
        return error(code=429, message='反馈提交过于频繁，请 1 分钟后再试')

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return bad_request('请求体必须为 JSON 对象')
    history_id = data.get('history_id')
    mark_type = data.get('mark_type', '')
    corrected_class = data.get('corrected_class', '')
    note = data.get('note', '')
    if isinstance(history_id, bool) or not isinstance(history_id, int) or history_id < 1:
        return bad_request('history_id 必须为正整数')
    if not all(isinstance(value, str) for value in (mark_type, corrected_class, note)):
        return bad_request('mark_type、corrected_class 和 note 必须为字符串')

    mark_type = mark_type.strip()
    corrected_class = corrected_class.strip()
    note = note.strip()
    if mark_type not in SamplePool.MARK_TYPES:
        return bad_request(f'mark_type 必须为 {"/".join(SamplePool.MARK_TYPES)}')
    if len(corrected_class) > MAX_CORRECTED_CLASS_LENGTH:
        return bad_request('corrected_class 长度不能超过 100 个字符')
    if len(note) > MAX_NOTE_LENGTH:
        return bad_request('note 长度不能超过 200 个字符')
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
        existed.status = SamplePool.STATUS_PENDING
        existed.review_note = None
        existed.reviewed_by = None
        existed.reviewed_at = None
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
    page, page_size = parse_pagination()

    pagination = SamplePool.query.filter_by(user_id=current_user.id) \
        .order_by(SamplePool.created_at.desc()) \
        .paginate(page=page, per_page=page_size, error_out=False)

    return success(data={
        'list': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size
    })
