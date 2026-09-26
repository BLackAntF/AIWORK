import random
import time
from flask import current_app


class LLMService:
    _instance = None
    _client = None

    MOCK_ANSWERS_BY_CATEGORY = {
        'disease_identification': [
            "根据您描述的症状，{context}的可能性较大。**主要识别特征**如下：\n- 叶片出现**黄褐色斑点**，逐渐扩大呈圆形或不规则形\n- 病斑中央颜色较浅，边缘有明显褐色晕圈\n- 潮湿时病斑背面产生灰色霉层\n\n建议结合实际图片进行进一步确认，或咨询专业植保人员。",
            "从症状描述判断，可能是{context}。**识别要点**：\n1. 初期叶片出现水渍状小斑点\n2. 后期发展为多角形病斑，受叶脉限制\n3. 严重时叶片枯黄脱落\n\n**与相似病害的区别**：\n- 区别于霜霉病：该病病斑较小，霉层颜色更深\n- 区别于炭疽病：病斑无轮纹状排列的小黑点",
            "您描述的情况符合{context}的典型表现。**典型症状**：\n- **部位**：主要危害叶片，也可侵染叶柄和茎秆\n- **形态**：病斑近圆形，直径2-10mm不等\n- **颜色**：中央灰白色，边缘褐色\n- **质地**：后期病斑易穿孔\n\n建议及时采取防治措施，防止扩散。",
            "经分析，疑似{context}。**诊断依据**：\n- 发病时期：多在高温高湿季节发生\n- 受害部位：中下部叶片先发病，逐渐向上蔓延\n- 典型症状：叶背产生白色粉状物，后期变灰白色\n\n如需确诊，建议采集病样进行实验室镜检。"
        ],
        'prevention_method': [
            "针对{context}，建议采取以下**综合防治措施**：\n\n**1. 农业防治**\n- 选用抗病品种，合理密植\n- 加强田间管理，及时整枝打杈\n- 科学施肥，增施磷钾肥，提高植株抗病力\n\n**2. 物理防治**\n- 及时清除病叶、病株，带出田外销毁\n- 通风降湿，避免叶面结露\n\n**3. 化学防治**\n- 发病初期：喷施 **75%百菌清可湿性粉剂 600倍液**\n- 发病较重：喷施 **25%嘧菌酯悬浮剂 1500倍液**\n- 每隔7-10天一次，连续2-3次\n\n**注意事项**：\n- 药剂要轮换使用，避免产生抗药性\n- 晴天上午施药，避开高温时段",
            "防治{context}的**关键技术方案**：\n\n### 预防阶段\n- 播种前进行种子消毒处理（温汤浸种或药剂拌种）\n- 苗床土壤消毒，减少初侵染源\n- 苗期喷施保护性杀菌剂1-2次\n\n### 发病初期\n- 首选药剂：**80%代森锰锌可湿性粉剂 800倍液**\n- 配合使用：**50%多菌灵可湿性粉剂 500倍液**\n- 施药方式：均匀喷雾，重点喷施叶片背面\n\n### 发病盛期\n- 治疗剂：**10%苯醚甲环唑水分散粒剂 2000倍液**\n- 或：**43%戊唑醇悬浮剂 3000倍液**\n- 7天一次，连用2-3次\n\n**安全间隔期**：7-14天（根据具体药剂而定）",
            "{context}的**绿色防控方案**：\n\n**生物防治**：\n- 使用 **枯草芽孢杆菌** 可湿性粉剂，每亩100-150g\n- 或 **木霉菌** 生物制剂，按说明使用\n- 每隔5-7天喷施一次，连续3次\n\n**物理防治**：\n- 悬挂黄板诱杀传毒媒介\n- 覆盖防虫网阻隔害虫\n- 及时摘除病叶深埋处理\n\n**农业措施**：\n- 轮作倒茬（与非寄主作物轮作2-3年）\n- 深翻晒土，减少土壤中菌源\n- 合理灌溉，避免大水漫灌\n\n**适用于绿色/有机种植基地**"
        ],
        'cultivation_technique': [
            "关于{context}的**栽培技术要点**：\n\n**一、土壤准备**\n- 选择土层深厚、疏松肥沃、排水良好的壤土或砂壤土\n- 土壤pH值保持在6.0-7.5之间\n- 每亩施腐熟有机肥3000-5000kg，复合肥50kg作基肥\n\n**二、播种与定植**\n- 适时播种，避免过早或过晚\n- 合理密植，根据品种特性确定种植密度\n- 定植后浇透定根水，促进缓苗\n\n**三、田间管理**\n- 及时中耕除草，保持土壤疏松\n- 合理追肥：苗期以氮肥为主，结果期增施磷钾肥\n- 水分管理：见干见湿，避免积水\n\n**四、植株调整**\n- 及时整枝打杈，改善通风透光条件\n- 适时摘除老叶、病叶，减少养分消耗",
            "**高产栽培技术** - {context}专题：\n\n### 培育壮苗\n1. **营养土配制**：园土:腐熟有机肥:草炭 = 4:3:3\n2. **播种**：均匀撒播，覆土0.5-1cm\n3. **苗期管理**：白天25-28℃，夜间15-18℃\n4. **分苗**：2叶1心时分苗，株行距8×8cm\n\n### 整地定植\n- 深翻细耙，做成小高畦，畦宽1.2m\n- 株距30-40cm，行距50-60cm\n- 每亩定植2500-3000株\n\n### 肥水管理\n- **浇水**：定植后蹲苗7-10天，坐果后加强肥水\n- **追肥**：\n  - 提苗肥：缓苗后追施尿素5-8kg/亩\n  - 膨果肥：果实膨大期追施复合肥20-25kg/亩\n  - 叶面肥：中后期喷施0.2%磷酸二氢钾2-3次\n\n### 病虫害防治\n- 坚持\"预防为主，综合防治\"的植保方针\n- 优先采用农业、物理、生物防治措施",
            "**设施栽培技术指南** - {context}：\n\n**环境调控**：\n- **温度**：白天24-28℃，夜间15-18℃\n- **湿度**：空气相对湿度60%-70%\n- **光照**：保证充足光照，及时揭盖草帘\n- **通风**：每日通风换气，降低棚内湿度\n\n**栽培方式**：\n- 高垄栽培，覆盖地膜\n- 滴灌浇水，避免大水漫灌\n- 吊蔓栽培，合理整枝\n\n**肥料管理**：\n- 基肥为主，追肥为辅\n- 增施生物菌肥，改善土壤微生物环境\n- 叶面追肥补充中微量元素\n\n**关键技术节点**：\n- 定植期：地温稳定在15℃以上\n- 开花坐果期：控制肥水，防止徒长\n- 果实膨大期：加强肥水供应"
        ],
        'general': [
            "您好！关于{context}的问题，我来为您解答。\n\n这是农业生产中比较常见的问题，建议从以下几个方面入手：\n1. **准确诊断**：先明确具体是什么问题，对症施策\n2. **预防为主**：加强日常管理，提高植株抗逆性\n3. **及时处理**：发现问题及早处理，防止扩大蔓延\n4. **综合防治**：多种措施配合使用，效果更佳\n\n如果您能提供更详细的信息（如作物品种、发病时间、具体症状图片等），我可以给出更有针对性的建议。",
            "感谢您的提问！关于{context}，以下是一些基础信息：\n\n**基本概念**：\n这是植物生长过程中可能遇到的一类问题，在适宜的环境条件下容易发生。\n\n**主要影响因素**：\n- 气候条件：温度、湿度、光照\n- 栽培管理：施肥、浇水、密度\n- 品种抗性：不同品种抗性差异明显\n\n**建议措施**：\n- 加强观察，及时发现异常\n- 保持良好的栽培环境\n- 必要时采取针对性防治措施\n\n希望对您有帮助！如有其他问题，欢迎继续提问。",
            "您咨询的{context}相关问题解答如下：\n\n**概述**\n这是一个综合性的农业技术问题，涉及品种选择、栽培管理、病虫害防治等多个方面。\n\n**核心原则**\n- 因地制宜：根据当地气候、土壤条件选择合适方案\n- 科学管理：按照作物生长规律进行田间管理\n- 绿色发展：优先采用绿色防控技术\n\n**获取更多帮助**\n- 查阅当地农业技术推广部门发布的技术资料\n- 咨询当地植保站或农业技术推广中心\n- 关注农业科技公众号获取最新技术信息\n\n祝您种植顺利！"
        ]
    }

    CATEGORY_KEYWORDS = {
        'disease_identification': ['识别', '判断', '诊断', '是什么病', '什么病害', '症状', '特征', '怎么看', '鉴定', '疑似'],
        'prevention_method': ['防治', '治疗', '怎么治', '用什么药', '打什么药', '预防', '治疗方法', '防控', '药剂', '杀菌', '怎么处理'],
        'cultivation_technique': ['栽培', '种植', '怎么种', '技术', '管理', '施肥', '浇水', '播种', '定植', '育苗', '田间管理', '高产', '方法']
    }

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

    def _classify_question(self, question):
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in question)
            category_scores[category] = score
        max_score = max(category_scores.values()) if category_scores else 0
        if max_score == 0:
            return 'general'
        best_categories = [c for c, s in category_scores.items() if s == max_score]
        return random.choice(best_categories)

    def _generate_mock_answer(self, question, knowledge_list=None, detection_context='', disease_profile=None):
        time.sleep(random.uniform(1.0, 2.0))

        if disease_profile:
            profile_text = f"""【病害档案】
病害名称：{disease_profile.get('disease_name', '未知')}
诱因：{disease_profile.get('causes', '未知')}
症状：{disease_profile.get('symptoms', '未知')}
预防措施：{disease_profile.get('prevention', '未知')}
治疗方案：{disease_profile.get('treatment', '未知')}
推荐药剂：{disease_profile.get('pesticides', '未知')}"""
            context_parts = [profile_text]
            if knowledge_list:
                context_parts.append(f"【相关知识】\n{chr(10).join(knowledge_list)}")
            if detection_context:
                context_parts.append(f"【检测结果】{detection_context}")
            full_context = chr(10).join(context_parts)
            context_text = disease_profile.get('disease_name', '植物病害')
        else:
            context_text = detection_context or "植物病害"
            full_context = context_text

        category = self._classify_question(question)
        templates = self.MOCK_ANSWERS_BY_CATEGORY.get(category, self.MOCK_ANSWERS_BY_CATEGORY['general'])
        answer_template = random.choice(templates)
        answer = answer_template.format(context=context_text)

        sources = []
        if knowledge_list:
            sources = [k[:30] + '...' if len(k) > 30 else k for k in knowledge_list[:3]]
        elif disease_profile:
            sources = [f"{disease_profile.get('disease_name', '病害档案')} - 病害详细资料"]
        else:
            sources = [
                "植物病害防治手册 - 常见病害识别与防治",
                "园艺栽培技术 - 病虫害防治篇",
                "农业技术推广 - 经济作物病害防治指南"
            ]

        return {
            'answer': answer,
            'sources': sources,
            'category': category,
            'disease_profile': disease_profile
        }

    def _build_messages(self, question, knowledge_list=None, detection_context='', disease_profile=None):
        """构建 LLM 消息列表（提示词构造，供普通/流式调用复用）"""
        context_parts = []

        if disease_profile:
            profile_text = f"""【病害档案】
病害名称：{disease_profile.get('disease_name', '未知')}
诱因：{disease_profile.get('causes', '未知')}
症状：{disease_profile.get('symptoms', '未知')}
预防措施：{disease_profile.get('prevention', '未知')}
治疗方案：{disease_profile.get('treatment', '未知')}
推荐药剂：{disease_profile.get('pesticides', '未知')}"""
            context_parts.append(profile_text)

        if knowledge_list:
            context_parts.append(f"【相关知识】\n{chr(10).join(knowledge_list)}")

        if detection_context:
            context_parts.append(f"【检测结果】{detection_context}")

        system_prompt = f"""你是「番茄卫士」农业植保助手，一位资深的番茄种植与植物病害防治专家。

## 你的职责
- 根据提供的【病害档案】、【相关知识】、【检测结果】三块上下文，回答用户关于番茄病虫害识别、防治、用药、栽培的问题。
- 上下文缺失时，坦诚说明，不得编造病害名称、药剂名称或数据。
- 回答必须基于上下文中的事实，语气专业、条理清晰、可直接指导用户操作。

## 输入上下文说明（按优先级）
1. 【检测结果】：AI 视觉模型对图片的实时检测输出，含病害名称与检测置信度，是你最应采信的现场证据。
2. 【病害档案】：针对检测出的病害整理的权威资料（诱因/症状/预防/治疗/推荐药剂）。
3. 【相关知识】：从知识库检索到的相关条目。
4. 若无任何上下文，仅凭你的通用知识回答，并建议用户提供更多信息。

## 输出格式要求（必须遵循的固定模板，使用 Markdown）
当存在检测结果或病害档案时，按以下结构输出；否则可自由组织，但仍需包含结论与建议：

### 诊断结论
判断结果，一句话说明。

### 置信度评估
- **检测置信度**：引用【检测结果】中的数值（如"视觉模型检出置信度 87.5%"）；无检测结果则省略此项。
- **判断置信度**：你对上述结论的把握程度，用 高/中/低 表述，并给出依据（如症状吻合度、上下文完整度）。

### 症状依据
结合病害档案中的典型症状与检测情况，简述关键判断依据；无档案时用通用知识说明。

### 防治方案
分条列出，至少包含：
- **农业防治**：栽培管理层面的预防措施
- **化学防治**：发病后的药剂处理（若档案无明确药剂，给出常见合规药剂并注明需以当地植保部门推荐为准）

### 药剂推荐
药剂名称 + 稀释倍数/浓度 + 施药方式 + 施药间隔（基于档案或知识库；不确定时明确提示）。

### 注意事项
安全间隔期、轮换用药防抗性、施药时机等提醒。

## 行为红线
- 上下文信息不足时，明确写"缺少 X 信息"，不得臆测填充。
- 不夸大疗效，不使用"根治""100%有效"等绝对化表述。
- 涉及严重疫情或不确定场景时，建议用户咨询当地植保站或农技专家。

以下是为本次回答提供的上下文：
{chr(10).join(context_parts) if context_parts else '（无额外上下文，请基于通用农业植保知识回答）'}
"""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

    def generate_answer(self, question, knowledge_list=None, detection_context='', disease_profile=None):
        """生成回答

        Args:
            question: 用户问题
            knowledge_list: 参考知识列表
            detection_context: 检测结果上下文
            disease_profile: 病害档案信息

        Returns:
            dict: {'answer': str, 'sources': list, 'disease_profile': dict}
        """
        if self._use_mock():
            return self._generate_mock_answer(question, knowledge_list, detection_context, disease_profile)

        client = self._get_client()
        messages = self._build_messages(question, knowledge_list, detection_context, disease_profile)

        try:
            response = client.chat.completions.create(
                model=current_app.config['LLM_MODEL'],
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                timeout=current_app.config['LLM_TIMEOUT_SECONDS']
            )
        except Exception as e:
            current_app.logger.error(f"LLM API调用失败: {str(e)}")
            if not current_app.config.get('LLM_FALLBACK_TO_MOCK', True):
                raise RuntimeError(f"LLM API调用失败: {str(e)}")

            result = self._generate_mock_answer(
                question, knowledge_list, detection_context, disease_profile
            )
            result['degraded'] = True
            return result

        answer = response.choices[0].message.content

        sources = [k[:50] + '...' for k in knowledge_list] if knowledge_list else []

        return {
            'answer': answer,
            'sources': sources,
            'disease_profile': disease_profile,
            'degraded': False
        }

    def _stream_mock_answer(self, question, knowledge_list=None, detection_context='', disease_profile=None):
        """mock 模式下的流式回答：按字符分段逐个产出，模拟真实逐字效果"""
        result = self._generate_mock_answer(
            question, knowledge_list, detection_context, disease_profile
        )
        answer = result['answer']
        chunk_size = 4
        for start in range(0, len(answer), chunk_size):
            yield {'type': 'delta', 'text': answer[start:start + chunk_size]}
            time.sleep(0.03)
        yield {
            'type': 'meta',
            'sources': result.get('sources', []),
            'degraded': True
        }

    def generate_answer_stream(self, question, knowledge_list=None, detection_context='', disease_profile=None):
        """流式生成回答

        Yields:
            dict: {'type': 'delta', 'text': str} 逐个文本片段；
                  最后一条为 {'type': 'meta', 'sources': list, 'degraded': bool}
        """
        if self._use_mock():
            yield from self._stream_mock_answer(
                question, knowledge_list, detection_context, disease_profile
            )
            return

        client = self._get_client()
        messages = self._build_messages(question, knowledge_list, detection_context, disease_profile)

        try:
            response = client.chat.completions.create(
                model=current_app.config['LLM_MODEL'],
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                timeout=current_app.config['LLM_TIMEOUT_SECONDS'],
                stream=True
            )
            for chunk in response:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield {'type': 'delta', 'text': delta}
        except Exception as e:
            current_app.logger.error(f"LLM API流式调用失败: {str(e)}")
            if not current_app.config.get('LLM_FALLBACK_TO_MOCK', True):
                raise RuntimeError(f"LLM API调用失败: {str(e)}")

            yield from self._stream_mock_answer(
                question, knowledge_list, detection_context, disease_profile
            )
            return

        sources = [k[:50] + '...' for k in knowledge_list] if knowledge_list else []
        yield {
            'type': 'meta',
            'sources': sources,
            'degraded': False
        }


llm_service = LLMService()
