import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """初始化数据库并补齐历史缺失字段。"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT,
                authors_json TEXT,
                year INTEGER,
                venue TEXT,
                abstract TEXT,
                keywords TEXT,
                contributions TEXT,
                ai_summary TEXT,
                raw_text TEXT,
                markdown_text TEXT,
                analysis_json TEXT,
                pdf_path TEXT NOT NULL,
                pdf_hash TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        columns = {
            row[1] for row in cursor.execute("PRAGMA table_info(papers)").fetchall()
        }
        required_columns = {
            "authors_json": "TEXT",
            "raw_text": "TEXT",
            "markdown_text": "TEXT",
            "analysis_json": "TEXT",
        }
        for column, column_type in required_columns.items():
            if column not in columns:
                cursor.execute(f"ALTER TABLE papers ADD COLUMN {column} {column_type}")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)")

        conn.commit()
        conn.close()

    def add_paper(
        self,
        pdf_path: str,
        title: Optional[str] = None,
        authors: Optional[str] = None,
        year: Optional[int] = None,
        venue: Optional[str] = None,
        abstract: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        contributions: Optional[List[str]] = None,
        ai_summary: Optional[str] = None,
        raw_text: Optional[str] = None,
        markdown_text: Optional[str] = None,
        authors_json: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
        meta: Optional[Any] = None,
    ) -> int:
        """添加论文，兼容旧调用方式和 metadata 对象调用方式。"""
        if meta is not None:
            title = title or getattr(meta, "title", None)
            abstract = abstract or getattr(meta, "abstract", None)
            year = year or self._normalize_year(getattr(meta, "year", None))
            venue = venue or getattr(meta, "venue", None)
            keywords = keywords or getattr(meta, "keywords", None)
            contributions = contributions or getattr(meta, "contributions", None)
            ai_summary = ai_summary or getattr(meta, "ai_summary", None)

            meta_authors = getattr(meta, "authors", None) or []
            if meta_authors and not authors_json:
                authors_json = json.dumps(
                    [
                        {
                            "name": getattr(author, "name", str(author)),
                            "affiliation": getattr(author, "affiliation", ""),
                        }
                        for author in meta_authors
                    ],
                    ensure_ascii=False,
                )
            if meta_authors and not authors:
                authors = ", ".join(
                    getattr(author, "name", str(author)) for author in meta_authors
                )

        title = (title or Path(pdf_path).stem).strip()
        authors = authors.strip() if isinstance(authors, str) else authors
        year = self._normalize_year(year)
        pdf_hash = self._compute_file_hash(pdf_path)
        analysis_json = json.dumps(analysis, ensure_ascii=False) if analysis else None

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO papers (
                    title, authors, authors_json, year, venue, abstract,
                    keywords, contributions, ai_summary, raw_text, markdown_text,
                    analysis_json, pdf_path, pdf_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    authors,
                    authors_json,
                    year,
                    venue,
                    abstract,
                    self._json_dumps(keywords),
                    self._json_dumps(contributions),
                    ai_summary,
                    raw_text,
                    markdown_text,
                    analysis_json,
                    pdf_path,
                    pdf_hash,
                ),
            )
            paper_id = cursor.lastrowid
            conn.commit()
            return paper_id
        except sqlite3.IntegrityError:
            cursor.execute("SELECT id FROM papers WHERE pdf_hash = ?", (pdf_hash,))
            row = cursor.fetchone()
            if not row:
                raise
            paper_id = row[0]
            cursor.execute(
                """
                UPDATE papers
                SET title = COALESCE(NULLIF(?, ''), title),
                    authors = COALESCE(?, authors),
                    authors_json = COALESCE(?, authors_json),
                    year = COALESCE(?, year),
                    venue = COALESCE(?, venue),
                    abstract = COALESCE(?, abstract),
                    keywords = COALESCE(?, keywords),
                    contributions = COALESCE(?, contributions),
                    ai_summary = COALESCE(?, ai_summary),
                    raw_text = COALESCE(?, raw_text),
                    markdown_text = COALESCE(?, markdown_text),
                    analysis_json = COALESCE(?, analysis_json),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    title,
                    authors,
                    authors_json,
                    year,
                    venue,
                    abstract,
                    self._json_dumps(keywords),
                    self._json_dumps(contributions),
                    ai_summary,
                    raw_text,
                    markdown_text,
                    analysis_json,
                    paper_id,
                ),
            )
            conn.commit()
            return paper_id
        finally:
            conn.close()

    def get_paper(self, paper_id: int) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        conn.close()
        return self._deserialize_row(row) if row else None

    def get_all_papers(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [self._deserialize_row(row) for row in rows]

    def get_paper_analysis(self, paper_id: int) -> Optional[Dict[str, Any]]:
        paper = self.get_paper(paper_id)
        if not paper:
            return None

        analysis = paper.get("analysis")
        if analysis:
            return analysis

        keywords = paper.get("keywords_list") or []
        contributions = paper.get("contributions_list") or []
        if not keywords and not contributions and not paper.get("abstract"):
            return None

        return {
            "keywords": keywords,
            "key_contributions": contributions,
            "main_findings": contributions,
            "research_question": paper.get("abstract", "")[:300],
            "methodology": "",
        }

    def save_paper_analysis(self, paper_id: int, analysis: Dict[str, Any]) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE papers
            SET analysis_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (json.dumps(analysis, ensure_ascii=False), paper_id),
        )
        conn.commit()
        conn.close()

    def _deserialize_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        result = dict(row)
        result["authors_list"] = self._json_loads(result.get("authors_json")) or []
        result["keywords_list"] = self._json_loads(result.get("keywords")) or []
        result["contributions_list"] = self._json_loads(result.get("contributions")) or []
        result["analysis"] = self._json_loads(result.get("analysis_json"))
        return result

    def _compute_file_hash(self, file_path: str) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _json_dumps(self, value: Optional[Any]) -> Optional[str]:
        if value in (None, "", []):
            return None
        return json.dumps(value, ensure_ascii=False)

    def _json_loads(self, value: Optional[str]) -> Optional[Any]:
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def _normalize_year(self, value: Optional[Any]) -> Optional[int]:
        if value in (None, "", 0):
            return None
        try:
            year = int(value)
        except (TypeError, ValueError):
            return None
        return year if year > 0 else None
