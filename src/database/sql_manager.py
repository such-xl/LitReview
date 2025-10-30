import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
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
        
        # 论文基本信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT,
                year INTEGER,
                venue TEXT,
                doi TEXT,
                arxiv_id TEXT,
                pdf_path TEXT NOT NULL,
                pdf_hash TEXT UNIQUE,
                raw_text TEXT,
                markdown_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # AI提取的信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER NOT NULL,
                research_question TEXT,
                methodology TEXT,
                main_findings TEXT,
                key_contributions TEXT,
                limitations TEXT,
                future_work TEXT,
                keywords TEXT,
                analyzed_by TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            )
        """)
        
        # 论文关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_paper_id INTEGER,
                target_paper_id INTEGER,
                relation_type TEXT,
                FOREIGN KEY (source_paper_id) REFERENCES papers(id),
                FOREIGN KEY (target_paper_id) REFERENCES papers(id)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_paper ON paper_analysis(paper_id)")
        
        conn.commit()
        conn.close()
    
    def add_paper(self, title: str, pdf_path: str, authors: Optional[str] = None,
                  year: Optional[int] = None, venue: Optional[str] = None,
                  raw_text: Optional[str] = None, markdown_text: Optional[str] = None) -> int:
        """添加论文"""
        pdf_hash = self._compute_file_hash(pdf_path)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO papers (title, authors, year, venue, pdf_path, pdf_hash, raw_text, markdown_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, authors, year, venue, pdf_path, pdf_hash, raw_text, markdown_text))
            
            paper_id = cursor.lastrowid
            conn.commit()
            return paper_id
        except sqlite3.IntegrityError:
            # 论文已存在
            cursor.execute("SELECT id FROM papers WHERE pdf_hash = ?", (pdf_hash,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def add_analysis(self, paper_id: int, analysis_data: Dict[str, Any], analyzed_by: str) -> int:
        """添加论文分析结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO paper_analysis 
            (paper_id, research_question, methodology, main_findings, key_contributions, 
             limitations, future_work, keywords, analyzed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_id,
            analysis_data.get('research_question'),
            analysis_data.get('methodology'),
            json.dumps(analysis_data.get('main_findings', [])),
            json.dumps(analysis_data.get('key_contributions', [])),
            json.dumps(analysis_data.get('limitations', [])),
            analysis_data.get('future_work'),
            json.dumps(analysis_data.get('keywords', [])),
            analyzed_by
        ))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    def get_paper(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """获取论文信息"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_papers(self) -> List[Dict[str, Any]]:
        """获取所有论文"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM papers ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_paper_analysis(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """获取论文分析结果"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM paper_analysis WHERE paper_id = ? ORDER BY analyzed_at DESC LIMIT 1", 
                      (paper_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            # 解析JSON字段
            for field in ['main_findings', 'key_contributions', 'limitations', 'keywords']:
                if result.get(field):
                    result[field] = json.loads(result[field])
            return result
        return None
    
    def _compute_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
