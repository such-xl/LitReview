EXTRACTION_PROMPT = """
请仔细阅读以下学术论文，并提取关键信息。以JSON格式返回：

论文内容：
{paper_text}

请提取以下信息：
1. research_question: 研究问题（1-2句话）
2. methodology: 研究方法（2-3句话）
3. main_findings: 主要发现（3-5个要点）
4. key_contributions: 核心贡献（2-3个要点）
5. limitations: 研究局限性（2-3个要点）
6. future_work: 未来研究方向（1-2句话）
7. keywords: 关键词（5-10个）

返回格式：
{{
  "research_question": "...",
  "methodology": "...",
  "main_findings": ["...", "..."],
  "key_contributions": ["...", "..."],
  "limitations": ["...", "..."],
  "future_work": "...",
  "keywords": ["...", "..."]
}}
"""

REVIEW_GENERATION_PROMPT = """
基于以下相关论文，撰写一篇结构化的文献综述。

研究主题：{topic}

相关论文：
{papers_info}

要求：
1. 按照以下结构组织：
   - 研究背景与动机
   - 主要研究方法分类
   - 研究发现与趋势
   - 现有研究的局限性
   - 未来研究方向

2. 每个部分：
   - 总结共同趋势和模式
   - 对比不同研究的观点
   - 引用具体论文支撑观点（使用[作者, 年份]格式）

3. 写作要求：
   - 学术正式语言
   - 逻辑清晰，层次分明
   - 客观中立，避免主观评价
   - 长度约1500-2000字

请开始撰写：
"""
