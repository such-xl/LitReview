from typing import Optional
from . import PDFParser
from .marker_parser import MarkerParser
from .pymupdf_parser import PyMuPDFParser
from .llm_parser import LLMParser
from .mineru_chunker import MinerUParser

class ParserFactory:
    @staticmethod
    def create_parser(parser_type: str = "pymupdf", llm_client=None, use_gpu=True) -> PDFParser:
        """创建PDF解析器
        
        Args:
            parser_type: 解析器类型 (pymupdf/marker/llm/mineru)
            llm_client: LLM客户端实例（parser_type="llm"时必需）
            use_gpu: 是否使用GPU（parser_type="mineru"时有效）
        """
        if parser_type == "llm":
            if llm_client is None:
                raise ValueError("LLM解析器需要提供llm_client参数")
            return LLMParser(llm_client)
        elif parser_type == "mineru":
            try:
                return MinerUParser(use_gpu=use_gpu)
            except Exception as e:
                print(f"MinerU初始化失败: {e}，回退到PyMuPDF")
                return PyMuPDFParser()
        elif parser_type == "marker":
            try:
                return MarkerParser()
            except ImportError:
                print("Marker未安装，回退到PyMuPDF")
                return PyMuPDFParser()
        elif parser_type == "pymupdf":
            print("使用PyMuPDF解析器")
            return PyMuPDFParser()
        else:
            raise ValueError(f"不支持的解析器类型: {parser_type}。支持: pymupdf/marker/llm/mineru")
