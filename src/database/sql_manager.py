import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from scripts.analyze_papers import ArticleMetadata
import hashlib
import json

class SQLManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 论文表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT,
                year INTEGER,
                venue TEXT,
                abstract TEXT,
                keywords TEXT,
                contributions TEXT,
                ai_summary TEXT,
                pdf_path TEXT NOT NULL,
                pdf_hash TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)")
        
        conn.commit()
        conn.close()
    
    def add_paper(self, pdf_path: str, meta: ArticleMetadata) -> int:
        """添加论文"""
        pdf_hash = self._compute_file_hash(pdf_path)
        
        # 序列化作者列表
        authors_json = json.dumps([a.dict() for a in meta.authors], ensure_ascii=False) if meta.authors else None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO papers (title, authors, year, venue, abstract, 
                                  keywords, contributions, ai_summary, pdf_path, pdf_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meta.title,
                authors_json,
                meta.year if meta.year > 0 else None,
                meta.venue,
                meta.abstract, 
                json.dumps(meta.keywords, ensure_ascii=False) if meta.keywords else None,
                json.dumps(meta.contributions, ensure_ascii=False) if meta.contributions else None,
                meta.ai_summary, 
                pdf_path, 
                pdf_hash
            ))
            
            paper_id = cursor.lastrowid
            conn.commit()
            return paper_id
        except sqlite3.IntegrityError:
            # 论文已存在
            cursor.execute("SELECT id FROM papers WHERE pdf_hash = ?", (pdf_hash,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def add_paper_from_metadata(self, metadata, pdf_path: str, 
                                raw_text: Optional[str] = None, 
                                markdown_text: Optional[str] = None) -> int:
        """从 ArticleMetadata 对象添加论文
        
        Args:
            metadata: ArticleMetadata 对象或字典
            pdf_path: PDF文件路径
            raw_text: 原始文本
            markdown_text: Markdown文本
        """
        # 处理作者列表
        authors_str = None
        authors_json = None
        if hasattr(metadata, 'authors') and metadata.authors:
            # 生成简单的作者字符串
            authors_str = ', '.join([a.name if hasattr(a, 'name') else str(a) for a in metadata.authors])
            # 保存完整的JSON
            authors_json = json.dumps(
                [{'name': a.name, 'affiliation': a.affiliation} if hasattr(a, 'name') 
                 else {'name': str(a), 'affiliation': ''} for a in metadata.authors],
                ensure_ascii=False
            )
        
        return self.add_paper(
            title=metadata.title if hasattr(metadata, 'title') else '',
            pdf_path=pdf_path,
            authors=authors_str,
            authors_json=authors_json,
            year=metadata.year if hasattr(metadata, 'year') and metadata.year > 0 else None,
            venue=metadata.venue if hasattr(metadata, 'venue') else None,
            abstract=metadata.abstract if hasattr(metadata, 'abstract') else None,
            keywords=metadata.keywords if hasattr(metadata, 'keywords') else None,
            contributions=metadata.contributions if hasattr(metadata, 'contributions') else None,
            ai_summary=metadata.ai_summary if hasattr(metadata, 'ai_summary') else None,
            raw_text=raw_text,
            markdown_text=markdown_text
        )
    
    def get_paper(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """获取论文信息"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            # 解析JSON字段
            if result.get('authors_json'):
                result['authors_list'] = json.loads(result['authors_json'])
            if result.get('keywords'):
                result['keywords_list'] = json.loads(result['keywords'])
            if result.get('contributions'):
                result['contributions_list'] = json.loads(result['contributions'])
            return result
        return None
    
    def get_all_papers(self) -> List[Dict[str, Any]]:
        """获取所有论文"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM papers ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            # 解析JSON字段
            if result.get('authors_json'):
                result['authors_list'] = json.loads(result['authors_json'])
            if result.get('keywords'):
                result['keywords_list'] = json.loads(result['keywords'])
            if result.get('contributions'):
                result['contributions_list'] = json.loads(result['contributions'])
            results.append(result)
        return results
    
    
    def _compute_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
if __name__ == "__main__":
    ...