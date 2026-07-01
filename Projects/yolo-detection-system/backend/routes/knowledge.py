import uuid
from flask import Blueprint, request
from models import ChatHistory, db
from utils.response import success, bad_request
from middleware.auth_middleware import login_required
from services.knowledge_service import knowledge_service
from services.llm_service import llm_service

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')


@knowledge_bp.route('/ask', methods=['POST'])
@login_required
def ask_question(current_user):
    """向知识库提问"""
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    detection_context = data.get('detection_context', '').strip()
    session_id = data.get('session_id', '').strip()

    if not question:
        return bad_request('问题不能为空')

    # 生成 session_id（如果没有提供）
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:12]}"

    # 搜索相关知识
    knowledge_list = knowledge_service.search(question, top_k=3)

    # 生成回答
    llm_result = llm_service.generate_answer(
        question=question,
        knowledge_list=knowledge_list,
        detection_context=detection_context
    )

    # 保存用户提问记录
    user_msg = ChatHistory(
        user_id=current_user.id,
        session_id=session_id,
        role='user',
        content=question
    )
    db.session.add(user_msg)

    # 保存助手回答记录
    assistant_msg = ChatHistory(
        user_id=current_user.id,
        session_id=session_id,
        role='assistant',
        content=llm_result['answer']
    )
    assistant_msg.set_metadata({
        'sources': llm_result.get('sources', []),
        'detection_context': detection_context
    })
    db.session.add(assistant_msg)

    db.session.commit()

    return success(data={
        'answer': llm_result['answer'],
        'sources': llm_result.get('sources', []),
        'session_id': session_id
    })


@knowledge_bp.route('/history', methods=['GET'])
@login_required
def get_chat_history(current_user):
    """获取对话历史"""
    session_id = request.args.get('session_id', '').strip()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = ChatHistory.query.filter_by(user_id=current_user.id)

    if session_id:
        query = query.filter_by(session_id=session_id)

    total = query.count()
    items = query.order_by(ChatHistory.created_at.asc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [item.to_dict() for item in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@knowledge_bp.route('/session/<session_id>', methods=['DELETE'])
@login_required
def delete_session(current_user, session_id):
    """删除指定会话的所有对话记录"""
    if not session_id:
        return bad_request('会话ID不能为空')

    deleted = ChatHistory.query.filter_by(
        user_id=current_user.id,
        session_id=session_id
    ).delete()
    db.session.commit()

    return success(message='对话已删除', data={'deleted_count': deleted})


@knowledge_bp.route('/sessions', methods=['GET'])
@login_required
def get_session_list(current_user):
    """获取会话列表"""
    # 查询所有不重复的 session_id 及其最新消息
    subquery = db.session.query(
        ChatHistory.session_id,
        db.func.max(ChatHistory.created_at).label('last_time')
    ).filter(
        ChatHistory.user_id == current_user.id,
        ChatHistory.session_id.isnot(None)
    ).group_by(ChatHistory.session_id).subquery()

    sessions = db.session.query(
        ChatHistory.session_id,
        ChatHistory.content,
        ChatHistory.created_at
    ).join(
        subquery,
        (ChatHistory.session_id == subquery.c.session_id) &
        (ChatHistory.created_at == subquery.c.last_time)
    ).order_by(subquery.c.last_time.desc()).all()

    session_list = []
    for session_id, last_content, last_time in sessions:
        session_list.append({
            'session_id': session_id,
            'last_message': last_content[:50] + '...' if len(last_content) > 50 else last_content,
            'last_time': last_time.isoformat() if last_time else None
        })

    return success(data={'sessions': session_list})


# ==================== 知识库管理接口（管理员） ====================

@knowledge_bp.route('/items', methods=['GET'])
@login_required
def list_knowledge(current_user):
    """获取知识库列表"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    category = request.args.get('category', '').strip() or None
    keyword = request.args.get('keyword', '').strip() or None

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    items, total = knowledge_service.list_knowledge(
        page=page,
        page_size=page_size,
        category=category,
        keyword=keyword
    )

    return success(data={
        'list': [item.to_dict() for item in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@knowledge_bp.route('/items/<int:kb_id>', methods=['GET'])
@login_required
def get_knowledge_detail(current_user, kb_id):
    """获取知识详情"""
    kb = knowledge_service.get_knowledge_by_id(kb_id)
    if not kb or not kb.is_active:
        return bad_request('知识不存在')

    return success(data=kb.to_dict())


@knowledge_bp.route('/categories', methods=['GET'])
@login_required
def get_categories(current_user):
    """获取知识分类列表"""
    categories = knowledge_service.get_categories()
    return success(data={'categories': categories})
