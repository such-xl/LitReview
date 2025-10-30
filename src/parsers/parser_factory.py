from . import PDFParser
from .marker_parser import MarkerParser
from .pymupdf_parser import PyMuPDFParser

class ParserFactory:
    @staticmethod
    def create_parser(parser_type: str = "pymupdf") -> PDFParser:
        """创建PDF解析器"""
        if parser_type == "marker":
            try:
                return MarkerParser()
            except ImportError:
                print("Marker未安装，回退到PyMuPDF")
                return PyMuPDFParser()
        elif parser_type == "pymupdf":
            print("使用PyMuPDF解析器")
            return PyMuPDFParser()
        else:
            raise ValueError(f"不支持的解析器类型: {parser_type}")
