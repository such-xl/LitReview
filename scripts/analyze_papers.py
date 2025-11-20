#!/usr/bin/env python3

# import sys
# from pathlib import Path
# from tqdm import tqdm

# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))

# from config import settings
# from src.database import SQLManager, VectorManager
# from src.llm.llm_factory import LLMFactory
# from src.analysis.extractor import PaperExtractor

import os
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types
import pathlib

class Author(BaseModel):
    name: str = Field(...)
    affiliation: str = Field("", description="Optional affiliation")

class ArticleMetadata(BaseModel):
    title: str = Field("", description="Full title of the paper")
    abstract: str = Field("", description="Abstract text")
    keywords: List[str] = Field(default_factory=list)
    authors: List[Author] = Field(default_factory=list)
    year: int = Field(0, description="Publication year, 0 if unknown")
    venue: str = Field("", description="Journal or conference name")
    contributions: List[str] = Field(default_factory=list)
    ai_summary: str = Field("", description="AI-generated short summary")

def analyze_paper(paper_path,api_key,proxy):
    """analyze sigle paper 分析整个PDF文档"""
    if proxy:
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy

    client = genai.Client(api_key=api_key)

    filepath = pathlib.Path(paper_path)

    prompt = """

        Extract the metadata from the following paper text. Output a single JSON object and nothing else that strictly follows this schema:
            - title (string)
            - abstract (string)
            - keywords (array of strings)
            - authors (array of objects with "name" and optional "affiliation")
            - year (integer)
            - venue (string)
            - contributions (array of short strings)
            - ai_summary (string, 2-4 sentences)
        Only use information present in the PDF. If a field is missing, return an empty string or empty array (not null).

    """
    pdf_part = types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type="application/pdf"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            pdf_part,
            types.Part(text=prompt)
        ],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": ArticleMetadata.model_json_schema()
        }
    )
    article = ArticleMetadata.model_validate_json(response.text)
    print(article)

if __name__ == "__main__":
    analyze_paper("/home/xiale/papers/mcp/data/pdfs/a.pdf",api_key="AIzaSyBYYHeJp7k4cCBcdbaJGTAnpvwmK_10O80",proxy='http://192.168.31.112:10807')
    
    """
    title='Curiosity-Driven Reinforcement Learning for Dynamic Flexible Job Shop Scheduling' 

    abstract="The dynamic flexible job shop scheduling (DFJSP) problem involves assigning appropriate jobs to available ma-chines in real time under uncertain conditions. Reinforcement learning (RL) approaches hold promise for adaptive schedul-ing but often suffers from sample inefficiency due to sparse and delayed rewards. This paper proposes a curiosity-driven RL framework for the DFJSP with stochastic job arrivals. A centralized policy sequentially activates machines to select jobs with the objective of minimizing total tardiness. The curiosity-based intrinsic reward is incorporated to alleviate the explo-ration deficiency by encouraging the agent to explore novel and informative states. This intrinsic motivation improves sample efficiency in dynamic and sparse-rewards environments. The performance gain depends on scenario characteristics: it is particularly pronounced in high-load, dynamic environments, while in low-load, more predictable settings, improvements are moderate. These findings highlight the framework's potential for adaptive, data-efficient scheduling under uncertainty." 

    keywords=['Dynamic Flexible Job Shop Scheduling', 'Reinforcement Learning', 'Intrinsic Motivation', 'Curiosity-Driven Learning', 'Stochastic Job Arrivals'] 

    authors=[Author(name='Le Xia', affiliation='School of Information Engineering, Jiangxi University of Science and Technology, Ganzhou 341000, China'), 
             Author(name='Tao Xu', affiliation='School of Information Engineering, Jiangxi University of Science and Technology, Ganzhou 341000, China'), 
             Author(name='Zhiwei Liu', affiliation='School of Information Engineering, Jiangxi University of Science and Technology, Ganzhou 341000, China'),
             Author(name='Bi Wang', affiliation='School of Information Engineering, Jiangxi University of Science and Technology, Ganzhou 341000, China; Jiangxi Provincial Key Laboratory of Multidimensional Intelligent Perception and Control, Ganzhou 341000, China')
             ] 
    year=2024 
    venue='' 
    contributions=['Proposed a curiosity-driven Reinforcement Learning (RL) framework for Dynamic Flexible Job Shop Scheduling (DFJSP) with stochastic job arrivals.', 'Incorporated a curiosity-based intrinsic reward to alleviate exploration deficiency and encourage novel and informative state exploration.', 'Demonstrated that intrinsic motivation consistently improves total tardiness and accelerates convergence compared to a baseline RL agent.', 'Showed that the relative effectiveness of intrinsic motivation mechanisms (ICM and RND) depends on system load and scenario characteristics (ICM for low-load, RND for high-load).'] 
    
    ai_summary='This paper introduces a curiosity-driven Reinforcement Learning (RL) framework for Dynamic Flexible Job Shop Scheduling (DFJSP) to address sample inefficiency from sparse and delayed rewards. By incorporating an intrinsic reward, the framework encourages exploration of novel states, improving sample efficiency and consistently reducing total tardiness. Experimental results indicate that curiosity-driven exploration, particularly with ICM or RND, effectively enhances adaptive and data-efficient scheduling under uncertainty, with their effectiveness varying based on system load conditions.'
    
    """
#     # 初始化
#     sql_manager = SQLManager(str(settings.sqlite_path))
#     vector_manager = VectorManager(str(settings.chroma_path))
    
#     # 创建LLM
#     llm = LLMFactory.create_llm(
#         provider=llm_provider,
#         model=model or settings.DEFAULT_LOCAL_MODEL,
#         base_url=settings.OLLAMA_BASE_URL
#     )
    
#     extractor = PaperExtractor(llm)
    
#     # 获取论文
#     paper = sql_manager.get_paper(paper_id)
#     if not paper:
#         print(f"论文不存在: {paper_id}")
#         return False
    
#     print(f"分析论文 (ID: {paper_id}): {paper['title']}")
    
#     # 提取信息
#     try:
#         analysis = extractor.extract_info(paper['raw_text'] or paper['markdown_text'])
        
#         # 保存分析结果
#         sql_manager.add_analysis(paper_id, analysis, f"{llm_provider}/{model or settings.DEFAULT_LOCAL_MODEL}")
        
#         print(f"✓ 分析完成")
#         print(f"  研究问题: {analysis['research_question'][:100]}...")
#         print(f"  关键词: {', '.join(analysis['keywords'][:5])}")
        
#         # 保存分析向量
#         analysis_text = f"""
# 研究问题: {analysis['research_question']}
# 方法: {analysis['methodology']}
# 主要发现: {' '.join(analysis['main_findings'])}
# 核心贡献: {' '.join(analysis['key_contributions'])}
# 关键词: {' '.join(analysis['keywords'])}
# """
#         vector_manager.add_analysis(paper_id, analysis_text, {
#             "paper_id": paper_id,
#             "title": paper['title']
#         })
        
#         return True
        
#     except Exception as e:
#         print(f"✗ 分析失败: {e}")
#         return False

# def analyze_all_papers(llm_provider: str = "ollama", model: str = None):
#     """分析所有未分析的论文"""
    
#     sql_manager = SQLManager(str(settings.sqlite_path))
    
#     # 获取所有论文
#     papers = sql_manager.get_all_papers()
    
#     if not papers:
#         print("没有找到论文")
#         return
    
#     print(f"找到 {len(papers)} 篇论文")
    
#     # 过滤已分析的论文
#     unanalyzed = []
#     for paper in papers:
#         analysis = sql_manager.get_paper_analysis(paper['id'])
#         if not analysis:
#             unanalyzed.append(paper)
    
#     if not unanalyzed:
#         print("所有论文都已分析")
#         return
    
#     print(f"需要分析 {len(unanalyzed)} 篇论文")
    
#     success_count = 0
#     for paper in tqdm(unanalyzed, desc="分析进度"):
#         if analyze_paper(paper['id'], llm_provider, model):
#             success_count += 1
    
#     print(f"\n分析完成: {success_count}/{len(unanalyzed)} 成功")

# def main():
#     import argparse
    
#     parser = argparse.ArgumentParser(description="分析论文并提取关键信息")
#     parser.add_argument("--paper-id", type=int, help="指定论文ID")
#     parser.add_argument("--all", action="store_true", help="分析所有未分析的论文")
#     parser.add_argument("--provider", default="ollama", 
#                        choices=["ollama", "openai", "claude"],
#                        help="LLM提供商 (默认: ollama)")
#     parser.add_argument("--model", help="模型名称")
    
#     args = parser.parse_args()
    
#     if args.paper_id:
#         analyze_paper(args.paper_id, args.provider, args.model)
#     elif args.all:
#         analyze_all_papers(args.provider, args.model)
#     else:
#         print("请指定 --paper-id 或 --all")
#         parser.print_help()

# if __name__ == "__main__":
#     main()

