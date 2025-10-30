from typing import Optional
from .llm_interface import LLMInterface
from .ollama_model import OllamaModel
from .litellm_model import LiteLLMModel
from .openai_compatible import OpenAICompatibleModel

class LLMFactory:
    @staticmethod
    def create_llm(
        provider: str = "ollama",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> LLMInterface:
        """创建LLM实例"""
        
        if provider == "ollama":
            model = model or "llama2"
            base_url = base_url or "http://localhost:11434"
            return OllamaModel(base_url=base_url, model=model)
        
        elif provider == "custom":
            # 使用OpenAI兼容API（不依赖LiteLLM）
            if not base_url or not api_key:
                raise ValueError("custom模式需要提供base_url和api_key")
            return OpenAICompatibleModel(model=model, api_key=api_key, base_url=base_url)
        
        elif provider in ["openai", "claude", "gpt-4", "gpt-3.5-turbo"]:
            # 使用LiteLLM支持多种API
            if provider == "openai" or provider.startswith("gpt"):
                model = model or provider if provider.startswith("gpt") else "gpt-3.5-turbo"
            elif provider == "claude":
                model = model or "claude-3-sonnet-20240229"
            
            return LiteLLMModel(model=model, api_key=api_key, base_url=base_url)
        
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
