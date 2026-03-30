from typing import Optional
from . import PDFParser
from .marker_parser import MarkerParser
from .pymupdf_parser import PyMuPDFParser
from .llm_parser import LLMParser
from .mineru_chunker import MinerUParser

class ParserFactory:
    @staticmethod
    def resolve_parser_order(parser_type: str) -> tuple[str, ...]:
        """返回给定策略下的解析器尝试顺序。"""
        if parser_type == "auto":
            return ("marker", "mineru", "pymupdf")
        return (parser_type,)

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
            return MinerUParser(use_gpu=use_gpu)
        elif parser_type == "marker":
            return MarkerParser()
        elif parser_type == "pymupdf":
            print("使用PyMuPDF解析器")
            return PyMuPDFParser()
        else:
            raise ValueError(f"不支持的解析器类型: {parser_type}。支持: auto/pymupdf/marker/llm/mineru")
