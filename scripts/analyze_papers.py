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
import pathlib
from config.settings import settings
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types

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

def analyze_paper(paper_path):
    """analyze sigle paper 分析整个PDF文档"""
    if settings.PROXY:
        os.environ['HTTP_PROXY'] = settings.PROXY
        os.environ['HTTPS_PROXY'] = settings.PROXY 

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

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
    print(response)
    print(type(article))
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

