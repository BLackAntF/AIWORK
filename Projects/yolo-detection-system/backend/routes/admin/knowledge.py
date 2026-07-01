from flask import request
from sqlalchemy import func
from routes.admin import admin_bp
from models import Knowledge, KnowledgeCategory, db
from utils.response import success, bad_request, not_found, error
from middleware.auth_middleware import admin_required
from services.knowledge_service import knowledge_service


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
        # 使用 func.concat 避免 SQL 注入
        query = query.filter(
            (Knowledge.title.like(func.concat('%', keyword, '%'))) |
            (Knowledge.content.like(func.concat('%', keyword, '%')))
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

    Body: { title, content, category?, source? }
    """
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category')
    source = data.get('source')

    if not title:
        return bad_request('标题不能为空')
    if not content:
        return bad_request('内容不能为空')

    kb = knowledge_service.add_knowledge(
        title=title,
        content=content,
        category=category,
        source=source
    )

    return success(data=kb.to_dict(), message='知识已创建')


@admin_bp.route('/knowledge/<int:kb_id>', methods=['PUT'])
@admin_required
def update_knowledge(current_user, kb_id):
    """编辑知识

    Body: { title?, content?, category?, is_active? }
    """
    kb = Knowledge.query.get(kb_id)
    if not kb:
        return not_found('知识不存在')

    data = request.get_json() or {}
    title = data.get('title')
    content = data.get('content')
    category = data.get('category')
    is_active = data.get('is_active')

    updated = knowledge_service.update_knowledge(
        kb_id=kb_id,
        title=title,
        content=content,
        category=category
    )

    if is_active is not None:
        kb.is_active = bool(is_active)
        db.session.commit()

    return success(data=updated.to_dict(), message='知识已更新')


@admin_bp.route('/knowledge/<int:kb_id>', methods=['DELETE'])
@admin_required
def delete_knowledge(current_user, kb_id):
    """删除知识（软删除 is_active=false）"""
    result = knowledge_service.delete_knowledge(kb_id)
    if not result:
        return not_found('知识不存在')

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
    """同步向量库（Mock）"""
    return success(message='向量库同步成功', data={'synced': True, 'count': 0})


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

    return success(message='分类已删除', data={'updated_knowledge': updated_count})
