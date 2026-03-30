import os
import json
from typing import Any, Dict, Optional

from .llm_interface import LLMInterface


class GeminiModel(LLMInterface):
    """Google Gemini模型"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", proxy: Optional[str] = None):
        try:
            from google import genai

            if proxy:
                os.environ["HTTP_PROXY"] = proxy
                os.environ["HTTPS_PROXY"] = proxy

            self.client = genai.Client(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("请安装: pip install -q -U google-genai")

    def test(self, prompt: str):
        response = self.client.models.generate_content(
            contents=prompt,
            model=self.model
        )
        return response.text

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> str:
        """生成文本"""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config=generation_config,
        )

        return response.text
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """返回结构化的JSON输出"""
        system_prompt = "你是一个专业的学术论文分析助手。请严格按照JSON格式返回结果。"
        full_prompt = f"{prompt}\n\n请以JSON格式返回，不要包含其他文字。"
        
        response = self.generate(full_prompt, system_prompt, temperature=0.1)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"无法解析JSON响应: {response}")
