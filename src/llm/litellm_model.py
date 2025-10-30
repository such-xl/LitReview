from typing import Optional, Dict, Any
import json
from .llm_interface import LLMInterface

class LiteLLMModel(LLMInterface):
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, base_url: Optional[str] = None):
        try:
            import litellm
            self.litellm = litellm
            self.model = model
            self.api_key = api_key
            self.base_url = base_url
        except ImportError:
            raise ImportError("请安装 litellm: pip install litellm")
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> str:
        """生成文本"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            if self.base_url:
                response = self.litellm.completion(
                    model=f"openai/{self.model}",
                    messages=messages,
                    api_base=self.base_url,
                    api_key=self.api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                response = self.litellm.completion(
                    model=self.model,
                    messages=messages,
                    api_key=self.api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
    
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
