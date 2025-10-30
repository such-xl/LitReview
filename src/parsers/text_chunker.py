from typing import List, Dict
import re

class TextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict[str, any]]:
        """将文本分块"""
        if not text:
            return []
        
        # 按段落分割
        paragraphs = self._split_paragraphs(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # 如果单个段落超过chunk_size，需要进一步分割
            if para_length > self.chunk_size:
                # 先保存当前chunk
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
                    current_chunk = []
                    current_length = 0
                
                # 分割长段落
                sub_chunks = self._split_long_paragraph(para)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk(sub_chunk, len(chunks), metadata))
            
            # 如果加上这个段落会超过chunk_size
            elif current_length + para_length > self.chunk_size:
                # 保存当前chunk
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
                
                # 开始新chunk，保留overlap
                if self.chunk_overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-1]
                    current_chunk = [overlap_text, para]
                    current_length = len(overlap_text) + para_length
                else:
                    current_chunk = [para]
                    current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # 保存最后一个chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
        
        return chunks
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """按段落分割文本"""
        # 按双换行符分割
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """分割长段落"""
        # 按句子分割
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _create_chunk(self, text: str, index: int, metadata: Dict = None) -> Dict:
        """创建chunk对象"""
        chunk = {
            "text": text,
            "index": index,
            "length": len(text)
        }
        
        if metadata:
            chunk["metadata"] = metadata
        
        return chunk
    
    def chunk_by_sections(self, sections: Dict[str, str], metadata: Dict = None) -> List[Dict[str, any]]:
        """按章节分块"""
        chunks = []
        
        for section_name, section_text in sections.items():
            section_metadata = metadata.copy() if metadata else {}
            section_metadata["section"] = section_name
            
            section_chunks = self.chunk_text(section_text, section_metadata)
            chunks.extend(section_chunks)
        
        return chunks
