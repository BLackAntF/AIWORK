from flask import request
from routes.admin import admin_bp
from models import Knowledge, KnowledgeCategory, Tag, KnowledgeTag, db
from utils.response import success, bad_request, not_found, error
from middleware.auth_middleware import admin_required
from services.knowledge_service import knowledge_service
from services import notification_service
from utils.audit import log_knowledge_action, log_category_action
from utils.html_utils import sanitize_html


@admin_bp.route('/knowledge', methods=['GET'])
@admin_required
def get_knowledge_list(current_user):
    """获取知识列表（分页、筛选）

    Query Params:
        page: 页码
        page_size: 每页数量
        category: 分类筛选
        keyword: 关键词搜索
        is_active: 状态筛选
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    category = request.args.get('category', '').strip()
    keyword = request.args.get('keyword', '').strip()
    is_active_str = request.args.get('is_active', '').strip()

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = Knowledge.query

    if category:
        query = query.filter(Knowledge.category == category)

    if keyword:
        # contains() 由 ORM 生成参数化的 LIKE，避免 SQL 注入且兼容 SQLite
        query = query.filter(
            Knowledge.title.contains(keyword) |
            Knowledge.content.contains(keyword)
        )

    if is_active_str == 'true':
        query = query.filter(Knowledge.is_active == True)
    elif is_active_str == 'false':
        query = query.filter(Knowledge.is_active == False)

    total = query.count()
    items = query.order_by(Knowledge.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [k.to_dict() for k in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@admin_bp.route('/knowledge/<int:kb_id>', methods=['GET'])
@admin_required
def get_knowledge_detail(current_user, kb_id):
    """获取知识详情"""
    kb = Knowledge.query.get(kb_id)
    if not kb:
        return not_found('知识不存在')

    return success(data=kb.to_dict())


@admin_bp.route('/knowledge', methods=['POST'])
@admin_required
def create_knowledge(current_user):
    """新增知识

    Body: { title, content, category?, source?, tag_ids?, summary? }
    """
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category')
    source = data.get('source')
    tag_ids = data.get('tag_ids', [])
    summary = data.get('summary', '').strip()

    if not title:
        return bad_request('标题不能为空')
    if not content:
        return bad_request('内容不能为空')

    sanitized_content = sanitize_html(content)

    kb = knowledge_service.add_knowledge(
        title=title,
        content=sanitized_content,
        category=category,
        source=source,
        summary=summary,
        tag_ids=tag_ids
    )

    log_knowledge_action(
        user_id=current_user.id,
        username=current_user.username,
        action='create_knowledge',
        knowledge_id=kb.id,
        detail=f"创建知识: {title}"
    )

    return success(data=kb.to_dict(), message='知识已创建')


@admin_bp.route('/knowledge/<int:kb_id>', methods=['PUT'])
@admin_required
def update_knowledge(current_user, kb_id):
    """编辑知识

    Body: { title?, content?, category?, is_active?, tag_ids?, summary? }
    """
    kb = Knowledge.query.get(kb_id)
    if not kb:
        return not_found('知识不存在')

    data = request.get_json() or {}
    title = data.get('title')
    content = data.get('content')
    category = data.get('category')
    is_active = data.get('is_active')
    tag_ids = data.get('tag_ids')
    summary = data.get('summary')

    if content:
        content = sanitize_html(content)

    updated = knowledge_service.update_knowledge(
        kb_id=kb_id,
        title=title,
        content=content,
        category=category,
        summary=summary,
        tag_ids=tag_ids
    )

    if is_active is not None:
        kb.is_active = bool(is_active)
        db.session.commit()

    log_knowledge_action(
        user_id=current_user.id,
        username=current_user.username,
        action='update_knowledge',
        knowledge_id=kb_id,
        detail=f"更新知识: {updated.title}"
    )

    return success(data=updated.to_dict(), message='知识已更新')


@admin_bp.route('/knowledge/<int:kb_id>', methods=['DELETE'])
@admin_required
def delete_knowledge(current_user, kb_id):
    """删除知识（软删除 is_active=false）"""
    kb = Knowledge.query.get(kb_id)
    if not kb:
        return not_found('知识不存在')

    kb_title = kb.title
    kb.is_active = False
    db.session.commit()

    log_knowledge_action(
        user_id=current_user.id,
        username=current_user.username,
        action='delete_knowledge',
        knowledge_id=kb_id,
        detail=f"删除知识: {kb_title}"
    )

    return success(message='知识已删除')


@admin_bp.route('/knowledge', methods=['DELETE'])
@admin_required
def batch_delete_knowledge(current_user):
    """批量删除知识

    Body: { ids: [] }
    """
    data = request.get_json() or {}
    ids = data.get('ids', [])

    if not ids or not isinstance(ids, list):
        return bad_request('ids 参数必须为非空数组')

    count = Knowledge.query.filter(Knowledge.id.in_(ids)).update(
        {Knowledge.is_active: False},
        synchronize_session=False
    )
    db.session.commit()

    log_knowledge_action(
        user_id=current_user.id,
        username=current_user.username,
        action='batch_delete_knowledge',
        knowledge_id=None,
        detail=f"批量删除 {count} 条知识, IDs: {ids}"
    )

    return success(message=f'已删除 {count} 条知识')


@admin_bp.route('/knowledge/import', methods=['POST'])
@admin_required
def import_knowledge(current_user):
    """批量导入知识（CSV/JSON 文件上传）"""
    file = request.files.get('file')
    if not file:
        return bad_request('请上传文件')

    filename = file.filename.lower()
    content = []

    try:
        if filename.endswith('.csv'):
            import csv
            import io
            file_content = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(file_content))
            for row in reader:
                title = row.get('title', '').strip()
                cont = row.get('content', '').strip()
                if title and cont:
                    content.append({
                        'title': title,
                        'content': cont,
                        'category': row.get('category'),
                        'source': row.get('source')
                    })
        elif filename.endswith('.json'):
            import json
            file_content = file.read().decode('utf-8')
            items = json.loads(file_content)
            for item in items:
                title = item.get('title', '').strip()
                cont = item.get('content', '').strip()
                if title and cont:
                    content.append({
                        'title': title,
                        'content': cont,
                        'category': item.get('category'),
                        'source': item.get('source')
                    })
        else:
            return bad_request('仅支持 CSV 和 JSON 格式文件')

        if not content:
            return bad_request('未找到有效数据')

        for item in content:
            knowledge_service.add_knowledge(**item)

        return success(message=f'成功导入 {len(content)} 条知识', data={'count': len(content)})

    except Exception as e:
        db.session.rollback()
        return error(message=f'导入失败: {str(e)}')


@admin_bp.route('/knowledge/sync-vector', methods=['POST'])
@admin_required
def sync_vector(current_user):
    """同步/重建 BM25 检索索引

    重新从数据库构建检索索引（本方案为进程内 BM25，检索时数据变更会自动懒重建，
    此接口用于主动重建并返回索引统计）。
    """
    result = knowledge_service.build_index()

    log_knowledge_action(
        user_id=current_user.id,
        username=current_user.username,
        action='sync_vector',
        knowledge_id=None,
        detail=f"重建检索索引：{result['synced_count']} 条，耗时 {result['elapsed_ms']}ms"
    )

    return success(message=f"索引同步完成，共 {result['synced_count']} 条知识", data=result)


@admin_bp.route('/categories', methods=['GET'])
@admin_required
def get_categories(current_user):
    """获取分类列表"""
    categories = KnowledgeCategory.query.order_by(KnowledgeCategory.created_at.asc()).all()
    return success(data=[c.to_dict() for c in categories])


@admin_bp.route('/categories', methods=['POST'])
@admin_required
def create_category(current_user):
    """新增分类

    Body: { name, description? }
    """
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip() or None

    if not name:
        return bad_request('分类名称不能为空')

    existing = KnowledgeCategory.query.filter_by(name=name).first()
    if existing:
        return bad_request('分类名称已存在')

    category = KnowledgeCategory(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    log_category_action(
        user_id=current_user.id,
        username=current_user.username,
        action='create_category',
        category_id=category.id,
        detail=f"创建分类: {name}"
    )

    return success(data=category.to_dict(), message='分类已创建')


@admin_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@admin_required
def update_category(current_user, cat_id):
    """修改分类"""
    category = KnowledgeCategory.query.get(cat_id)
    if not category:
        return not_found('分类不存在')

    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')

    old_name = category.name
    if name:
        name = name.strip()
        if not name:
            return bad_request('分类名称不能为空')
        existing = KnowledgeCategory.query.filter_by(name=name).first()
        if existing and existing.id != cat_id:
            return bad_request('分类名称已存在')
        category.name = name

    if description is not None:
        category.description = description.strip() or None

    db.session.commit()

    log_category_action(
        user_id=current_user.id,
        username=current_user.username,
        action='update_category',
        category_id=cat_id,
        detail=f"更新分类: {old_name} -> {category.name}"
    )

    return success(data=category.to_dict(), message='分类已更新')


@admin_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@admin_required
def delete_category(current_user, cat_id):
    """删除分类（该分类下知识的 category 设为 null）"""
    category = KnowledgeCategory.query.get(cat_id)
    if not category:
        return not_found('分类不存在')

    cat_name = category.name
    updated_count = Knowledge.query.filter_by(category=cat_name).update(
        {Knowledge.category: None},
        synchronize_session=False
    )

    db.session.delete(category)
    db.session.commit()

    log_category_action(
        user_id=current_user.id,
        username=current_user.username,
        action='delete_category',
        category_id=cat_id,
        detail=f"删除分类: {cat_name}，更新了 {updated_count} 条知识"
    )

    return success(message='分类已删除', data={'updated_knowledge': updated_count})


@admin_bp.route('/knowledge/tags', methods=['GET'])
@admin_required
def get_tags(current_user):
    """获取标签列表"""
    tags = Tag.query.order_by(Tag.created_at.desc()).all()
    return success(data=[t.to_dict() for t in tags])


@admin_bp.route('/knowledge/tags', methods=['POST'])
@admin_required
def create_tag(current_user):
    """新增标签

    Body: { name, color? }
    """
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    color = data.get('color', 'primary').strip()

    if not name:
        return bad_request('标签名称不能为空')

    existing = Tag.query.filter_by(name=name).first()
    if existing:
        return bad_request('标签名称已存在')

    tag = Tag(name=name, color=color)
    db.session.add(tag)
    db.session.commit()

    return success(data=tag.to_dict(), message='标签已创建')


@admin_bp.route('/knowledge/tags/<int:tag_id>', methods=['PUT'])
@admin_required
def update_tag(current_user, tag_id):
    """修改标签

    Body: { name?, color? }
    """
    tag = Tag.query.get(tag_id)
    if not tag:
        return not_found('标签不存在')

    data = request.get_json() or {}
    name = data.get('name')
    color = data.get('color')

    if name:
        name = name.strip()
        if not name:
            return bad_request('标签名称不能为空')
        existing = Tag.query.filter_by(name=name).first()
        if existing and existing.id != tag_id:
            return bad_request('标签名称已存在')
        tag.name = name

    if color:
        tag.color = color.strip()

    db.session.commit()

    return success(data=tag.to_dict(), message='标签已更新')


@admin_bp.route('/knowledge/tags/<int:tag_id>', methods=['DELETE'])
@admin_required
def delete_tag(current_user, tag_id):
    """删除标签"""
    tag = Tag.query.get(tag_id)
    if not tag:
        return not_found('标签不存在')

    tag_name = tag.name
    KnowledgeTag.query.filter_by(tag_id=tag_id).delete()
    db.session.delete(tag)
    db.session.commit()

    return success(message='标签已删除', data={'deleted_tag': tag_name})


@admin_bp.route('/knowledge/upload', methods=['POST'])
@admin_required
def upload_knowledge_admin(current_user):
    """管理员上传文件创建知识（直接生效）"""
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

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'uploads', 'knowledge')
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
        
        kb.status = 'active'
        kb.uploader_id = current_user.id
        kb.file_path = save_path
        db.session.commit()

        log_knowledge_action(
            user_id=current_user.id,
            username=current_user.username,
            action='upload_knowledge',
            knowledge_id=kb.id,
            detail=f"上传文件创建知识: {parsed['title']}"
        )

        return success(data=kb.to_dict(), message='知识已创建')

    except Exception as e:
        db.session.rollback()
        return error(message=f'上传失败: {str(e)}')


@admin_bp.route('/knowledge/pending', methods=['GET'])
@admin_required
def get_pending_knowledge(current_user):
    """获取待审核知识列表"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = Knowledge.query.filter(Knowledge.status == 'pending')
    total = query.count()
    items = query.order_by(Knowledge.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [k.to_dict() for k in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@admin_bp.route('/knowledge/pending/<int:kb_id>', methods=['PUT'])
@admin_required
def approve_knowledge(current_user, kb_id):
    """审核知识（通过/拒绝）"""
    kb = Knowledge.query.get(kb_id)
    if not kb:
        return not_found('知识不存在')
    if kb.status != 'pending':
        return bad_request('该知识状态不是待审核')

    data = request.get_json() or {}
    action = data.get('action', 'approve')

    if action == 'approve':
        kb.status = 'active'
        kb.is_active = True
        message = '审核通过'
    elif action == 'reject':
        kb.status = 'rejected'
        message = '已拒绝'
    else:
        return bad_request('无效的审核操作')

    db.session.commit()

    # 通知投稿人审核结果（匿名/无投稿人时跳过）
    if kb.uploader_id:
        notification_service.notify_knowledge_review(
            user_id=kb.uploader_id,
            kb_id=kb.id,
            title=kb.title,
            approved=action == 'approve'
        )
        db.session.commit()

    log_knowledge_action(
        user_id=current_user.id,
        username=current_user.username,
        action=f'approve_knowledge_{action}',
        knowledge_id=kb_id,
        detail=f"{message}: {kb.title}"
    )

    return success(data=kb.to_dict(), message=message)
