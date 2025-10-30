from typing import Optional, Dict, Any
import json
from .llm_interface import LLMInterface

class OllamaModel(LLMInterface):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        try:
            import ollama
            self.client = ollama.Client(host=base_url)
            self.model = model
        except ImportError:
            raise ImportError("请安装 ollama: pip install ollama")
    
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
        
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )
        
        return response['message']['content']
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """返回结构化的JSON输出"""
        system_prompt = "你是一个专业的学术论文分析助手。请严格按照JSON格式返回结果。"
        
        full_prompt = f"{prompt}\n\n请以JSON格式返回，不要包含其他文字。"
        
        response = self.generate(full_prompt, system_prompt, temperature=0.1)
        
        # 提取JSON
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取JSON块
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"无法解析JSON响应: {response}")
