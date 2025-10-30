import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path

class VectorManager:
    def __init__(self, db_path: str, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 创建集合
        self.fulltext_collection = self.client.get_or_create_collection(
            name="paper_fulltext",
            metadata={"description": "Full text embeddings for semantic search"}
        )
        
        self.abstract_collection = self.client.get_or_create_collection(
            name="paper_abstracts",
            metadata={"description": "Abstract embeddings for quick retrieval"}
        )
        
        self.analysis_collection = self.client.get_or_create_collection(
            name="paper_analysis",
            metadata={"description": "AI-extracted information embeddings"}
        )
    
    def add_fulltext(self, paper_id: int, text_chunks: List[str], metadatas: Optional[List[Dict]] = None):
        """添加全文向量"""
        ids = [f"paper_{paper_id}_chunk_{i}" for i in range(len(text_chunks))]
        
        if metadatas is None:
            metadatas = [{"paper_id": paper_id, "chunk_index": i} for i in range(len(text_chunks))]
        
        self.fulltext_collection.add(
            documents=text_chunks,
            ids=ids,
            metadatas=metadatas
        )
    
    def add_abstract(self, paper_id: int, abstract: str, metadata: Optional[Dict] = None):
        """添加摘要向量"""
        if metadata is None:
            metadata = {"paper_id": paper_id}
        
        self.abstract_collection.add(
            documents=[abstract],
            ids=[f"paper_{paper_id}_abstract"],
            metadatas=[metadata]
        )
    
    def add_analysis(self, paper_id: int, analysis_text: str, metadata: Optional[Dict] = None):
        """添加分析信息向量"""
        if metadata is None:
            metadata = {"paper_id": paper_id}
        
        self.analysis_collection.add(
            documents=[analysis_text],
            ids=[f"paper_{paper_id}_analysis"],
            metadatas=[metadata]
        )
    
    def search_fulltext(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """搜索全文"""
        results = self.fulltext_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def search_abstracts(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """搜索摘要"""
        results = self.abstract_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def search_analysis(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """搜索分析信息"""
        results = self.analysis_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def delete_paper(self, paper_id: int):
        """删除论文的所有向量"""
        # 删除全文
        try:
            self.fulltext_collection.delete(where={"paper_id": paper_id})
        except:
            pass
        
        # 删除摘要
        try:
            self.abstract_collection.delete(ids=[f"paper_{paper_id}_abstract"])
        except:
            pass
        
        # 删除分析
        try:
            self.analysis_collection.delete(ids=[f"paper_{paper_id}_analysis"])
        except:
            pass
