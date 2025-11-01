"""测试 MinerU 解析器"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers import ParserFactory, MinerUParser, ParsedPaper

class TestMinerUParser:
    """测试 MinerU 解析器"""
    
    def test_create_parser(self):
        """测试通过工厂创建解析器"""
        parser = ParserFactory.create_parser("mineru", use_gpu=False)
        assert isinstance(parser, MinerUParser)
    
    def test_parser_with_gpu(self):
        """测试 GPU 配置"""
        parser = MinerUParser(use_gpu=True)
        assert parser is not None
    
    def test_parser_without_gpu(self):
        """测试 CPU 配置"""
        parser = MinerUParser(use_gpu=False)
        assert parser.use_gpu == False
    
    @pytest.mark.skipif(not Path("data/pdfs/a.pdf").exists(), 
                        reason="测试 PDF 文件不存在")
    def test_parse_pdf(self):
        """测试解析 PDF"""
        parser = MinerUParser(use_gpu=False)
        result = parser.parse("data/pdfs/a.pdf")
        
        assert isinstance(result, ParsedPaper)
        assert result.title
        assert result.full_text
        assert len(result.authors) > 0
    
    def test_extract_title(self):
        """测试标题提取"""
        parser = MinerUParser(use_gpu=False)
        text = "Deep Learning for Computer Vision\nAuthors: John Doe"
        title = parser._extract_title(text)
        assert "Deep Learning" in title
    
    def test_extract_abstract(self):
        """测试摘要提取"""
        parser = MinerUParser(use_gpu=False)
        text = """
        Title
        Abstract
        This is the abstract content.
        
        Introduction
        """
        abstract = parser._extract_abstract(text)
        assert "abstract content" in abstract.lower()
    
    def test_extract_sections(self):
        """测试章节提取"""
        parser = MinerUParser(use_gpu=False)
        text = """
        Introduction
        This is intro.
        
        Method
        This is method.
        """
        sections = parser._extract_sections(text)
        assert len(sections) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
