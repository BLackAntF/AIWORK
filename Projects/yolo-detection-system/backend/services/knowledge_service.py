import random
from flask import current_app
from sqlalchemy import func
from models import Knowledge, db


class KnowledgeService:
    """知识库服务

    负责知识库的管理和检索，开发环境暂不接入向量数据库，使用关键词匹配
    """
    _instance = None
    _collection = None

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

    def search(self, query, top_k=3):
        """搜索相关知识

        开发环境使用关键词模糊匹配，生产环境接入向量数据库

        Args:
            query: 查询内容
            top_k: 返回数量

        Returns:
            list: 知识内容列表
        """
        # 开发环境：使用 SQL LIKE 进行关键词匹配
        all_knowledge = Knowledge.query.filter_by(is_active=True).all()

        # 简单的关键词匹配打分
        scored = []
        query_lower = query.lower()
        for kb in all_knowledge:
            score = 0
            title_lower = kb.title.lower()
            content_lower = kb.content.lower()

            if query_lower in title_lower:
                score += 10
            if query_lower in content_lower:
                score += 5

            # 部分关键词匹配
            keywords = query_lower.split()
            for kw in keywords:
                if kw in title_lower:
                    score += 3
                if kw in content_lower:
                    score += 1

            if score > 0:
                scored.append((score, kb.content, kb.title))

        # 按分数排序
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]

        # 如果没有匹配结果，返回部分随机知识
        if not results and all_knowledge:
            selected = random.sample(all_knowledge, min(top_k, len(all_knowledge)))
            results = [kb.content for kb in selected]

        return results

    def search_with_titles(self, query, top_k=3):
        """搜索相关知识，返回标题和内容

        Args:
            query: 查询内容
            top_k: 返回数量

        Returns:
            list: [{'title': ..., 'content': ...}, ...]
        """
        all_knowledge = Knowledge.query.filter_by(is_active=True).all()

        scored = []
        query_lower = query.lower()
        for kb in all_knowledge:
            score = 0
            title_lower = kb.title.lower()
            content_lower = kb.content.lower()

            if query_lower in title_lower:
                score += 10
            if query_lower in content_lower:
                score += 5

            if score > 0:
                scored.append((score, kb))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [{'title': item[1].title, 'content': item[1].content}
                   for item in scored[:top_k]]

        if not results and all_knowledge:
            selected = random.sample(all_knowledge, min(top_k, len(all_knowledge)))
            results = [{'title': kb.title, 'content': kb.content} for kb in selected]

        return results

    def add_knowledge(self, title, content, category=None, source=None):
        """添加知识条目

        Args:
            title: 标题
            content: 内容
            category: 分类
            source: 来源

        Returns:
            Knowledge: 知识对象
        """
        kb = Knowledge(
            title=title,
            content=content,
            category=category,
            source=source
        )
        db.session.add(kb)
        db.session.commit()
        return kb

    def update_knowledge(self, kb_id, title=None, content=None, category=None, source=None):
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

    def list_knowledge(self, page=1, page_size=20, category=None, keyword=None):
        """获取知识列表

        Args:
            page: 页码
            page_size: 每页数量
            category: 分类筛选
            keyword: 关键词搜索

        Returns:
            tuple: (list, total)
        """
        query = Knowledge.query.filter_by(is_active=True)

        if category:
            query = query.filter(Knowledge.category == category)

        if keyword:
            # 使用 func.concat 避免 SQL 注入
            query = query.filter(
                (Knowledge.title.like(func.concat('%', keyword, '%'))) |
                (Knowledge.content.like(func.concat('%', keyword, '%')))
            )

        total = query.count()
        items = query.order_by(Knowledge.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return items, total

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


knowledge_service = KnowledgeService()
