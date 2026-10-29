from flask import Blueprint, request
from models import Knowledge, KnowledgeFavorite, Tag, db, iso_utc
from utils.response import success, not_found, bad_request, error
from services.knowledge_service import knowledge_service
from middleware.auth_middleware import login_required
from utils.params import parse_pagination

knowledge_user_bp = Blueprint('knowledge_user', __name__, url_prefix='/api/knowledge')


@knowledge_user_bp.route('/tags', methods=['GET'])
def get_tags():
    """获取标签列表（公开接口）"""
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return success(data=[t.to_dict() for t in tags])


@knowledge_user_bp.route('/favorites', methods=['GET'])
@login_required
def get_my_favorites(current_user):
    """获取我的收藏列表（需登录）

    Query Params:
        page: 页码，默认1
        page_size: 每页数量，默认12
    """
    page, page_size = parse_pagination(default_page_size=12)

    query = KnowledgeFavorite.query.filter_by(user_id=current_user.id)

    total = query.count()
    favorites = query.order_by(KnowledgeFavorite.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for fav in favorites:
        kb = fav.knowledge
        items.append({
            'id': fav.id,
            'knowledge_id': fav.knowledge_id,
            'created_at': iso_utc(fav.created_at),
            'knowledge': {
                'id': kb.id if kb else None,
                'title': kb.title if kb else '',
                'category': kb.category if kb else '',
                'summary': kb.summary if kb else ''
            } if kb else None
        })

    return success(data={
        'list': items,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@knowledge_user_bp.route('/<int:knowledge_id>/favorite', methods=['POST'])
@login_required
def add_favorite(current_user, knowledge_id):
    """收藏知识（需登录）"""
    knowledge = Knowledge.query.filter_by(
        id=knowledge_id,
        is_active=True
    ).first()

    if not knowledge:
        return not_found('知识不存在')

    exists = KnowledgeFavorite.query.filter_by(
        user_id=current_user.id,
        knowledge_id=knowledge_id
    ).first()

    if exists:
        return bad_request('已收藏')

    try:
        fav = KnowledgeFavorite(user_id=current_user.id, knowledge_id=knowledge_id)
        db.session.add(fav)
        db.session.commit()
        return success(data=fav.to_dict(), message='收藏成功')
    except Exception as e:
        db.session.rollback()
        return error(message=f'收藏失败: {str(e)}')


@knowledge_user_bp.route('/<int:knowledge_id>/favorite', methods=['DELETE'])
@login_required
def remove_favorite(current_user, knowledge_id):
    """取消收藏知识（需登录）"""
    fav = KnowledgeFavorite.query.filter_by(
        user_id=current_user.id,
        knowledge_id=knowledge_id
    ).first()

    if not fav:
        return not_found('未收藏')

    try:
        db.session.delete(fav)
        db.session.commit()
        return success(message='已取消收藏')
    except Exception as e:
        db.session.rollback()
        return error(message=f'取消收藏失败: {str(e)}')


@knowledge_user_bp.route('/<int:knowledge_id>/favorite-status', methods=['GET'])
@login_required
def get_favorite_status(current_user, knowledge_id):
    """查询知识收藏状态（需登录）"""
    exists = KnowledgeFavorite.query.filter_by(
        user_id=current_user.id,
        knowledge_id=knowledge_id
    ).first()

    return success(data={
        'is_favorite': exists is not None
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
