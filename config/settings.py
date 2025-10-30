from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # 数据库配置
    SQLITE_DB_PATH: str = "data/database/papers.db"
    CHROMA_DB_PATH: str = "data/database/chroma"
    
    # LLM配置
    DEFAULT_LLM_PROVIDER: str = "ollama"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_LOCAL_MODEL: str = "llama2"
    
    # 嵌入模型配置
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"
    
    # PDF解析配置
    PDF_PARSER: str = "marker"
    
    # 其他配置
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.3
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"
        extra = "allow"
    
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent
    
    @property
    def sqlite_path(self) -> Path:
        return self.project_root / self.SQLITE_DB_PATH
    
    @property
    def chroma_path(self) -> Path:
        return self.project_root / self.CHROMA_DB_PATH

settings = Settings()
