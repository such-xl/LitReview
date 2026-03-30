import os
import pathlib
from typing import List

from pydantic import BaseModel, Field

from config.settings import settings

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
        os.environ["HTTP_PROXY"] = settings.PROXY
        os.environ["HTTPS_PROXY"] = settings.PROXY

    from google import genai
    from google.genai import types

    if not settings.GEMINI_API_KEY:
        raise ValueError("缺少 GEMINI_API_KEY，请在环境变量或 .env 中配置。")
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
    return article

if __name__ == "__main__":
    raise SystemExit("这是一个库脚本，请从其他模块导入 analyze_paper() 调用。")
