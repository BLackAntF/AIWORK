from flask import Blueprint, request
from models import Knowledge, db
from utils.response import success, not_found, bad_request, error
from services.knowledge_service import knowledge_service
from middleware.auth_middleware import login_required

knowledge_user_bp = Blueprint('knowledge_user', __name__, url_prefix='/api/knowledge')

CATEGORIES = [
    {"value": "disease", "label": "病害识别"},
    {"value": "method", "label": "防治方法"},
    {"value": "cultivation", "label": "栽培技术"},
    {"value": "knowledge", "label": "基础知识"}
]


@knowledge_user_bp.route('/list', methods=['GET'])
def get_knowledge_list():
    """获取知识列表（公开接口）"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 12))
    category = request.args.get('category', '').strip()
    keyword = request.args.get('keyword', '').strip()

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 12

    items, total = knowledge_service.list_knowledge(
        page=page,
        page_size=page_size,
        category=category if category else None,
        keyword=keyword if keyword else None,
        is_public=True
    )

    return success(data={
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@knowledge_user_bp.route('/<int:knowledge_id>', methods=['GET'])
def get_knowledge_detail(knowledge_id):
    """获取知识详情（公开接口，自动增加阅读量）"""
    knowledge = Knowledge.query.filter_by(
        id=knowledge_id,
        is_active=True
    ).first()

    if not knowledge:
        return not_found('知识不存在')

    knowledge.views = (knowledge.views or 0) + 1
    db.session.commit()

    return success(data={
        'id': knowledge.id,
        'title': knowledge.title,
        'category': knowledge.category,
        'summary': knowledge.summary,
        'content': knowledge.content,
        'views': knowledge.views,
        'created_at': knowledge.created_at.isoformat() if knowledge.created_at else None
    })


@knowledge_user_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取分类列表（公开接口）"""
    return success(data={
        'categories': CATEGORIES
    })


@knowledge_user_bp.route('/<int:knowledge_id>/related', methods=['GET'])
def get_related_knowledge(knowledge_id):
    """获取相关知识（公开接口）

    Query Params:
        limit: 返回数量，默认5
    """
    kb = Knowledge.query.filter_by(
        id=knowledge_id,
        is_active=True
    ).first()

    if not kb:
        return not_found('知识不存在')

    limit = int(request.args.get('limit', 5))
    if limit < 1:
        limit = 5
    if limit > 20:
        limit = 20

    related = knowledge_service.get_related_knowledge(knowledge_id, limit=limit)

    return success(data={
        'list': related,
        'total': len(related)
    })


@knowledge_user_bp.route('/upload', methods=['POST'])
@login_required
def upload_knowledge_user(current_user):
    """用户上传文件创建知识（需审核）"""
    import os
    from services.file_parser import parse_file, ALLOWED_EXTENSIONS
    from utils.file_utils import save_uploaded_file

    file = request.files.get('file')
    if not file:
        return bad_request('请上传文件')

    filename = file.filename.lower()
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext not in ALLOWED_EXTENSIONS:
        return bad_request(f'不支持的文件格式，支持: {", ".join(ALLOWED_EXTENSIONS)}')

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads', 'knowledge')
    os.makedirs(upload_dir, exist_ok=True)

    try:
        save_path, new_filename, original_name = save_uploaded_file(file, upload_dir, 'kb_')

        parsed = parse_file(save_path, original_filename=original_name)
        
        category = request.form.get('category')
        source = request.form.get('source')
        tag_ids = request.form.get('tag_ids')
        tag_ids = [int(t) for t in tag_ids.split(',') if t.strip()] if tag_ids else []

        kb = knowledge_service.add_knowledge(
            title=parsed['title'],
            content=parsed['content'],
            category=category,
            source=source,
            summary=parsed['summary'],
            tag_ids=tag_ids
        )
        
        kb.status = 'pending'
        kb.uploader_id = current_user.id
        kb.file_path = save_path
        kb.is_active = False
        db.session.commit()

        return success(data={
            'id': kb.id,
            'title': kb.title,
            'status': kb.status
        }, message='上传成功，等待管理员审核')

    except Exception as e:
        db.session.rollback()
        return error(message=f'上传失败: {str(e)}')
