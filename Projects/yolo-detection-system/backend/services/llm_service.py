import random
from flask import current_app


class LLMService:
    """LLM 大模型问答服务

    开发环境使用 mock 数据，生产环境接入真实 API
    """
    _instance = None
    _client = None

    # Mock 回答模板
    MOCK_ANSWERS = [
        "根据检测结果和知识库分析，您提到的症状可能是{context}。建议采取以下措施：1. 及时清除受感染的叶片并集中销毁；2. 适当通风降湿；3. 可选用多菌灵或百菌清等药剂进行防治，每隔7-10天喷施一次，连续2-3次。",
        "您好，从描述来看可能是{context}。这是一种常见的植物病害，主要由真菌引起。防治建议：1. 加强栽培管理，合理施肥；2. 保持良好通风；3. 发病初期及时喷施代森锰锌或甲基托布津等杀菌剂。",
        "根据您提供的检测结果，初步判断为{context}。处理方案：1. 隔离病株防止传播；2. 剪除病叶并销毁；3. 使用对应药剂防治；4. 注意环境卫生，减少菌源。",
        "检测结果显示存在{context}的情况。建议您：1. 改善环境条件，避免高温高湿；2. 定期巡查，早发现早防治；3. 化学防治可选嘧菌酯、吡唑醚菌酯等药剂；4. 注意轮换用药，避免抗药性。"
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _use_mock(self):
        """是否使用 mock 数据"""
        return current_app.config.get('LLM_USE_MOCK', True)

    def _get_client(self):
        """获取 LLM 客户端（生产环境使用）"""
        if self._client is None:
            api_key = current_app.config['LLM_API_KEY']
            base_url = current_app.config['LLM_BASE_URL']
            if not api_key:
                raise ValueError("LLM_API_KEY 未配置")

            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=api_key, base_url=base_url)
            except ImportError:
                raise RuntimeError("openai 未安装，请先安装: pip install openai")

        return self._client

    def _generate_mock_answer(self, question, knowledge_list=None, detection_context=''):
        """生成 mock 回答"""
        context_text = detection_context or "植物病害"
        answer_template = random.choice(self.MOCK_ANSWERS)
        answer = answer_template.format(context=context_text)

        # 生成模拟来源
        sources = []
        if knowledge_list:
            sources = [k[:30] + '...' if len(k) > 30 else k for k in knowledge_list[:3]]
        else:
            sources = [
                "植物病害防治手册 - 常见病害识别与防治",
                "园艺栽培技术 - 病虫害防治篇",
                "农业技术推广 - 经济作物病害防治指南"
            ]

        return {
            'answer': answer,
            'sources': sources
        }

    def generate_answer(self, question, knowledge_list=None, detection_context=''):
        """生成回答

        Args:
            question: 用户问题
            knowledge_list: 参考知识列表
            detection_context: 检测结果上下文

        Returns:
            dict: {'answer': str, 'sources': list}
        """
        if self._use_mock():
            return self._generate_mock_answer(question, knowledge_list, detection_context)

        # 真实 LLM 调用
        client = self._get_client()

        # 构建提示词
        knowledge_text = '\n'.join(knowledge_list) if knowledge_list else ''
        context_parts = []
        if knowledge_text:
            context_parts.append(f"参考知识：\n{knowledge_text}")
        if detection_context:
            context_parts.append(f"检测结果：{detection_context}")

        system_prompt = f"""你是一个专业的植物病害诊断助手，请根据参考知识回答用户的问题。
回答要准确、专业，尽量结合提供的参考知识。
如果参考知识中没有相关内容，请如实说明。
{chr(10).join(context_parts)}
"""

        response = client.chat.completions.create(
            model=current_app.config['LLM_MODEL'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        answer = response.choices[0].message.content
        sources = [k[:50] + '...' for k in knowledge_list] if knowledge_list else []

        return {
            'answer': answer,
            'sources': sources
        }


llm_service = LLMService()
