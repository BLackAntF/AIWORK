from flask import current_app
from sqlalchemy import func, desc
from models import Knowledge, Tag, KnowledgeTag, db

try:
    import jieba
except ImportError:
    jieba = None
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


def _build_bm25_index(corpus, docs):
    """构建 BM25 索引（无 rank_bm25 时回退到文档列表原样存储）"""
    if BM25Okapi is not None:
        return BM25Okapi(corpus)
    return docs


# 病害领域常用词，确保 jieba 正确切分（如"早疫病"不被拆散）
_DISEASE_TERMS = [
    '早疫病', '晚疫病', '灰霉病', '白粉病', '霜霉病', '叶霉病', '病毒病',
    '青枯病', '枯萎病', '根腐病', '炭疽病', '疮痂病', '脐腐病', '脐橙病',
    '细菌性', '真菌性', '生理性', '黑斑病', '褐斑病', '斑枯病', '叶斑病',
    '疮痂', '根结线虫', '红蜘蛛', '蚜虫', '白粉虱', '潜叶蛾', '棉铃虫',
    '防治', '药剂', '轮作', '抗病品种', '种子处理', '生物防治', '化学防治'
]

# 口语查询 → 专业术语 同义映射（用户问"叶子发黄"，知识库里写的是"叶片黄化"）
_SYNONYM_MAP = {
    '叶子': '叶片', '叶面': '叶片',
    '发黄': '黄化', '变黄': '黄化', '泛黄': '黄化', '发黄斑': '黄化',
    '斑点': '病斑', '黑点': '黑斑', '水渍': '水渍状',
    '发霉': '霉变', '长毛': '霉变', '腐烂': '腐烂',
    '萎': '萎蔫', '枯死': '枯死', '干枯': '干枯',
    '打药': '药剂', '用药': '药剂', '农药': '药剂',
    '虫': '虫害', '虫子': '虫害', '红蜘蛛': '红蜘蛛',
    '喷': '喷雾', '治': '防治'
}


def _ensure_jieba():
    """初始化 jieba：注册领域词典（幂等）"""
    if jieba is None:
        return None
    if not getattr(_ensure_jieba, '_ready', False):
        for term in _DISEASE_TERMS:
            jieba.add_word(term)
        _ensure_jieba._ready = True
    return jieba


def _tokenize(text):
    """中文分词，保留长度>=2 的实义词"""
    jieba_engine = _ensure_jieba()
    if jieba_engine is None:
        return [t for t in text.lower().replace('，', ' ').replace('。', ' ').split() if len(t) >= 2]
    tokens = []
    for tok in jieba_engine.cut(text.lower()):
        tok = tok.strip()
        if len(tok) >= 2:
            tokens.append(tok)
    return tokens


def _expand_synonyms(tokens):
    """对查询词做同义扩展：口语词归一为专业术语（保留原词 + 映射词）"""
    expanded = []
    for tok in tokens:
        mapped = _SYNONYM_MAP.get(tok, tok)
        if mapped != tok:
            expanded.append(tok)
        expanded.append(mapped)
    return expanded


class KnowledgeService:
    """知识库服务

    检索实现：中文分词 + BM25 + 标题/分类加权。
    - 无需向量数据库 / embedding 服务 / 本地模型，纯 Python 实现
    - 开发环境关键词模糊匹配为兜底
    """
    _instance = None
    _collection = None
    # BM25 进程内索引缓存：key 为 (max_updated_at, total, total_chars) 组合签名
    _bm25_index = None
    _bm25_corpus = None
    _bm25_docs = None
    _bm25_signature = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_collection(self):
        """获取向量集合（生产环境使用）"""
        if self._collection is None:
            chroma_path = current_app.config['CHROMA_PATH']
            collection_name = current_app.config['CHROMA_COLLECTION']
            try:
                import chromadb
                client = chromadb.PersistentClient(path=chroma_path)
                self._collection = client.get_or_create_collection(name=collection_name)
            except ImportError:
                raise RuntimeError("chromadb 未安装，请先安装: pip install chromadb")
        return self._collection

    def _index_signature(self, all_knowledge):
        """计算知识快照签名：数据有变化时索引自动重建"""
        total = len(all_knowledge)
        max_updated = max((kb.updated_at or kb.created_at or 0 for kb in all_knowledge), default=0)
        total_chars = sum(len(kb.content or '') for kb in all_knowledge)
        return (total, total_chars, max_updated)

    def build_index(self):
        """重建 BM25 内存索引

        重新从数据库读取全部激活知识，构建分词语料与 BM25 索引。
        检索时若数据签名变化会自动懒重建；此方法用于主动同步（管理端"同步索引"）。

        Returns:
            dict: {synced, count, synced_count, elapsed_ms, method}
        """
        import time
        start = time.time()
        all_knowledge = self._active_knowledge()
        corpus, index = self._build_index(all_knowledge)
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            'synced': True,
            'count': len(corpus),
            'synced_count': len(corpus),
            'elapsed_ms': elapsed_ms,
            'method': 'bm25'
        }

    def _build_index(self, all_knowledge):
        """构建语料与 BM25 索引（无数据时返回空）"""
        corpus = self._build_corpus(all_knowledge)
        index = _build_bm25_index(corpus, all_knowledge) if corpus else None
        return corpus, index

    def _build_corpus(self, all_knowledge):
        """构建 BM25 语料：标题 token 复制两份实现加权，正文一份"""
        corpus = []
        for kb in all_knowledge:
            title_tokens = _tokenize(kb.title or '')
            content_tokens = _tokenize(kb.content or '')
            corpus.append(title_tokens + title_tokens + content_tokens)
        return corpus

    def _get_snapshot(self):
        """取激活知识快照，并按需重建缓存索引"""
        all_knowledge = self._active_knowledge()
        signature = self._index_signature(all_knowledge)
        if self._bm25_signature != signature:
            self._bm25_docs = all_knowledge
            self._bm25_corpus, self._bm25_index = self._build_index(all_knowledge)
            self._bm25_signature = signature
        return self._bm25_docs, self._bm25_corpus, self._bm25_index

    def _rank(self, query_tokens, top_k=3):
        """用缓存索引打分排序，返回 [(score, kb), ...]"""
        all_knowledge, corpus, index = self._get_snapshot()
        if index is not None and corpus:
            scores = index.get_scores(query_tokens)
        else:
            scores = self._fallback_scores(all_knowledge, query_tokens)

        ranked = list(zip(scores, all_knowledge))
        ranked.sort(key=lambda x: x[0], reverse=True)

        # BM25 全 0（无命中）时，按浏览量降序兜底，避免随机
        if ranked and ranked[0][0] <= 0:
            ranked.sort(key=lambda x: (x[1].views or 0), reverse=True)

        return ranked

    def _fallback_scores(self, all_knowledge, query_tokens):
        """无 rank_bm25 时的朴素打分（标题命中加权）"""
        scores = []
        for kb in all_knowledge:
            score = 0
            title_lower = (kb.title or '').lower()
            content_lower = (kb.content or '').lower()
            for tok in query_tokens:
                if tok in title_lower:
                    score += 10
                elif tok in content_lower:
                    score += 5
            scores.append(score)
        return scores

    def _active_knowledge(self):
        """获取检索候选：排除测试/临时数据（也过滤掉 is_inactive）"""
        return Knowledge.query.filter(
            Knowledge.is_active == True,
            ~Knowledge.category.in_(['测试分类', 'test', '测试']),
            ~Knowledge.title.like('test%'),
            ~Knowledge.title.like('tmp%'),
            ~Knowledge.title.like('kb_%')
        ).all()

    def search(self, query, top_k=3):
        """搜索相关知识

        基于 BM25 的中文检索：jieba 分词 + 同义扩展 + 标题加权。
        无命中时按浏览量兜底返回。

        Args:
            query: 查询内容
            top_k: 返回数量

        Returns:
            list: 知识内容列表
        """
        all_knowledge = self._active_knowledge()
        if not all_knowledge:
            return []

        raw_tokens = _tokenize(query)
        query_tokens = _expand_synonyms(raw_tokens) or raw_tokens

        ranked = self._rank(query_tokens, top_k)
        return [item[1].content for item in ranked[:top_k]]

    def search_with_titles(self, query, top_k=3):
        """搜索相关知识，返回标题和内容

        Args:
            query: 查询内容
            top_k: 返回数量

        Returns:
            list: [{'title': ..., 'content': ...}, ...]
        """
        all_knowledge = self._active_knowledge()
        if not all_knowledge:
            return []

        raw_tokens = _tokenize(query)
        query_tokens = _expand_synonyms(raw_tokens) or raw_tokens

        ranked = self._rank(query_tokens, top_k)

        return [{'title': item[1].title, 'content': item[1].content}
                for item in ranked[:top_k]]

    def add_knowledge(self, title, content, category=None, source=None, summary=None, tag_ids=None):
        """添加知识条目

        Args:
            title: 标题
            content: 内容
            category: 分类
            source: 来源
            summary: 摘要
            tag_ids: 标签ID列表

        Returns:
            Knowledge: 知识对象
        """
        kb = Knowledge(
            title=title,
            content=content,
            category=category,
            source=source,
            summary=summary
        )
        db.session.add(kb)
        db.session.flush()

        if tag_ids and isinstance(tag_ids, list):
            for tag_id in tag_ids:
                tag = Tag.query.get(tag_id)
                if tag:
                    kt = KnowledgeTag(knowledge_id=kb.id, tag_id=tag.id)
                    db.session.add(kt)

        db.session.commit()
        return kb

    def update_knowledge(self, kb_id, title=None, content=None, category=None, source=None, summary=None, tag_ids=None):
        """更新知识条目"""
        kb = Knowledge.query.get(kb_id)
        if not kb:
            return None

        if title is not None:
            kb.title = title
        if content is not None:
            kb.content = content
        if category is not None:
            kb.category = category
        if source is not None:
            kb.source = source
        if summary is not None:
            kb.summary = summary

        if tag_ids is not None and isinstance(tag_ids, list):
            KnowledgeTag.query.filter_by(knowledge_id=kb_id).delete()
            for tag_id in tag_ids:
                tag = Tag.query.get(tag_id)
                if tag:
                    kt = KnowledgeTag(knowledge_id=kb.id, tag_id=tag.id)
                    db.session.add(kt)

        db.session.commit()
        return kb

    def delete_knowledge(self, kb_id):
        """删除知识条目（软删除，设置 is_active=False）"""
        kb = Knowledge.query.get(kb_id)
        if not kb:
            return False

        kb.is_active = False
        db.session.commit()
        return True

    def list_knowledge(self, page=1, page_size=20, category=None, keyword=None, is_public=False):
        """获取知识列表

        Args:
            page: 页码
            page_size: 每页数量
            category: 分类筛选
            keyword: 关键词搜索
            is_public: 是否为用户端（返回简化字段）

        Returns:
            tuple: (list, total)
        """
        query = Knowledge.query.filter_by(is_active=True)

        if category:
            query = query.filter(Knowledge.category == category)

        if keyword:
            keyword_pattern = f'%{keyword}%'
            query = query.filter(
                (Knowledge.title.like(keyword_pattern)) |
                (Knowledge.content.like(keyword_pattern))
            )

        total = query.count()
        items = query.order_by(Knowledge.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        if is_public:
            return [self._to_public_dict(item) for item in items], total

        return items, total

    def _to_public_dict(self, knowledge):
        """转换为用户端字典格式"""
        return {
            'id': knowledge.id,
            'title': knowledge.title,
            'category': knowledge.category,
            'summary': knowledge.summary,
            'views': knowledge.views,
            'created_at': knowledge.created_at.isoformat() if knowledge.created_at else None
        }

    def get_knowledge_by_id(self, kb_id):
        """根据ID获取知识条目"""
        return Knowledge.query.get(kb_id)

    def get_categories(self):
        """获取所有分类"""
        results = db.session.query(Knowledge.category) \
            .filter(Knowledge.is_active == True, Knowledge.category.isnot(None)) \
            .distinct() \
            .all()
        return [r[0] for r in results if r[0]]

    def get_related_knowledge(self, kb_id, limit=5):
        """获取相关知识（基于共同标签数量排序）

        Args:
            kb_id: 知识ID
            limit: 返回数量

        Returns:
            list: 相关知识列表
        """
        kb = Knowledge.query.get(kb_id)
        if not kb:
            return []

        current_tag_ids = [t.id for t in kb.tags]

        if not current_tag_ids:
            recent = Knowledge.query.filter(
                Knowledge.is_active == True,
                Knowledge.id != kb_id
            ).order_by(desc(Knowledge.created_at)).limit(limit).all()
            return [self._to_related_dict(k) for k in recent]

        subq = db.session.query(
            KnowledgeTag.knowledge_id,
            func.count(KnowledgeTag.tag_id).label('common_count')
        ).filter(
            KnowledgeTag.tag_id.in_(current_tag_ids),
            KnowledgeTag.knowledge_id != kb_id
        ).group_by(KnowledgeTag.knowledge_id).subquery()

        results = db.session.query(Knowledge, subq.c.common_count).join(
            subq, Knowledge.id == subq.c.knowledge_id
        ).filter(
            Knowledge.is_active == True
        ).order_by(
            desc(subq.c.common_count),
            desc(Knowledge.created_at)
        ).limit(limit).all()

        related = []
        for kb_item, count in results:
            item_dict = self._to_related_dict(kb_item)
            item_dict['common_tags_count'] = count
            related.append(item_dict)

        if len(related) < limit:
            existing_ids = [r['id'] for r in related]
            recent = Knowledge.query.filter(
                Knowledge.is_active == True,
                Knowledge.id != kb_id,
                ~Knowledge.id.in_(existing_ids)
            ).order_by(desc(Knowledge.created_at)).limit(limit - len(related)).all()
            for k in recent:
                item_dict = self._to_related_dict(k)
                item_dict['common_tags_count'] = 0
                related.append(item_dict)

        return related

    def _to_related_dict(self, knowledge):
        """转换为相关知识字典格式"""
        return {
            'id': knowledge.id,
            'title': knowledge.title,
            'category': knowledge.category,
            'summary': knowledge.summary,
            'views': knowledge.views,
            'tags': [t.to_dict() for t in knowledge.tags] if knowledge.tags else [],
            'created_at': knowledge.created_at.isoformat() if knowledge.created_at else None
        }


knowledge_service = KnowledgeService()
