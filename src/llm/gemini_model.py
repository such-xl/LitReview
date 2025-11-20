from typing import Optional, Dict, Any
import json
from .llm_interface import LLMInterface
import os
from pydantic import BaseModel
from google.genai import types

# Define the desired output structure using Pydantic
class Recipe(BaseModel):
    recipe_name: str
    description: str
    ingredients: list[str]
    steps: list[str]
# from google import genai
# os.environ['HTTP_PROXY'] = 'http://192.168.31.112:10807'
# os.environ['HTTPS_PROXY'] = 'http://192.168.31.112:10807' 
# # The client gets the API key from the environment variable `GEMINI_API_KEY`.
# client = genai.Client(api_key='AIzaSyBYYHeJp7k4cCBcdbaJGTAnpvwmK_10O80')

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response)
# print(response.text)
class GeminiModel(LLMInterface):
    """Google Gemini模型"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", proxy: Optional[str] = None):
        try:
            from google import genai
            
            if proxy:
                os.environ['HTTP_PROXY'] = proxy
                os.environ['HTTPS_PROXY'] = proxy
            
            self.client = genai.Client(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("请安装: pip install -q -U google-genai")
    def test(self, prompt:str):
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
        
        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config
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
