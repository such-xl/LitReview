from dataclasses import dataclass
from typing import List, Dict
from abc import ABC, abstractmethod

@dataclass
class ParsedPaper:
    title: str
    authors: List[str]
    abstract: str
    full_text: str
    markdown_text: str
    sections: Dict[str, str]
    tables: List[Dict]
    equations: List[str]
    references: List[str]

class PDFParser(ABC):
    @abstractmethod
    def parse(self, pdf_path: str) -> ParsedPaper:
        pass

from .parser_factory import ParserFactory
from .text_chunker import TextChunker
from .mineru_chunker import MinerUParser, MinerUChunker

__all__ = ['ParsedPaper', 'PDFParser', 'ParserFactory', 'TextChunker', 'MinerUParser', 'MinerUChunker']
