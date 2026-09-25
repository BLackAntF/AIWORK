from flask import Blueprint, request
from models import DiseaseProfile
from utils.response import success, not_found
from middleware.auth_middleware import login_required

disease_bp = Blueprint('disease', __name__, url_prefix='/api/disease-profiles')

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _parse_pagination() -> tuple:
    """解析分页参数

    Returns:
        tuple: (page, page_size)
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        return 1, DEFAULT_PAGE_SIZE

    if page < 1:
        page = 1
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        page_size = DEFAULT_PAGE_SIZE
    return page, page_size


@disease_bp.route('', methods=['GET'])
@login_required
def list_disease_profiles(current_user) -> tuple:
    """获取病害档案列表

    Query:
        keyword: 按病害名称模糊匹配
        page: 页码，默认 1
        page_size: 每页条数，1..100，默认 20
    """
    page, page_size = _parse_pagination()
    keyword = request.args.get('keyword', '').strip() or None

    query = DiseaseProfile.query.filter_by(is_active=True)
    if keyword:
        # contains() 由 ORM 生成参数化的 LIKE，避免 SQL 注入且兼容 SQLite
        query = query.filter(DiseaseProfile.disease_name.contains(keyword))

    total = query.count()
    items = query.order_by(DiseaseProfile.class_id.asc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [item.to_dict() for item in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@disease_bp.route('/<int:class_id>', methods=['GET'])
@login_required
def get_disease_profile(current_user, class_id: int) -> tuple:
    """按病害类别 ID 获取档案详情（含发生规律）

    Args:
        class_id: 病害类别 ID
    """
    profile = DiseaseProfile.query.filter_by(
        class_id=class_id,
        is_active=True
    ).first()

    if not profile:
        return not_found('病害档案不存在')

    return success(data=profile.to_dict())