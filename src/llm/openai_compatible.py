from typing import Optional, Dict, Any
import json
import requests
from .llm_interface import LLMInterface

class OpenAICompatibleModel(LLMInterface):
    """OpenAI兼容API模型（不依赖LiteLLM）"""
    
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
    
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
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            
            # 检查HTTP状态
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
            
            # 检查响应内容
            if not response.text:
                raise Exception("服务器返回空响应")
            
            # 解析JSON
            try:
                result = response.json()
            except json.JSONDecodeError:
                raise Exception(f"API返回非JSON格式: {response.text[:500]}")
            
            # 提取内容
            if 'choices' not in result or not result['choices']:
                raise Exception(f"响应格式错误: {result}")
            
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            if "API" in str(e) or "HTTP" in str(e) or "响应" in str(e) or "服务器" in str(e):
                raise
            raise Exception(f"未知错误: {str(e)}")
    
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
