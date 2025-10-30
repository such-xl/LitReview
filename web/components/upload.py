import streamlit as st
from pathlib import Path
import tempfile
from src.parsers import ParserFactory, TextChunker
from config import settings

def render_upload_page():
    st.header("📤 上传论文")
    
    st.markdown("上传PDF论文文件，系统将自动解析并创建索引。")
    
    parser_type = st.selectbox("选择解析器", ["pymupdf", "marker"])
    
    uploaded_files = st.file_uploader(
        "选择PDF文件",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("开始导入", type="primary"):
        progress_bar = st.progress(0)
        success_count = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            tmp_path = None
            try:
                # 创建临时文件并写入
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                
                parser = ParserFactory.create_parser(parser_type)
                parsed = parser.parse(tmp_path)
                
                paper_id = st.session_state.sql_manager.add_paper(
                    title=parsed.title,
                    pdf_path=tmp_path,
                    authors=', '.join(parsed.authors),
                    raw_text=parsed.full_text,
                    markdown_text=parsed.markdown_text
                )
                
                chunker = TextChunker(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                chunks = chunker.chunk_text(parsed.full_text, {"paper_id": paper_id})
                
                if chunks:
                    chunk_texts = [chunk["text"] for chunk in chunks]
                    st.session_state.vector_manager.add_fulltext(paper_id, chunk_texts)
                
                success_count += 1
                
            except Exception as e:
                st.error(f"处理 {uploaded_file.name} 失败: {e}")
            finally:
                # 清理临时文件
                if tmp_path and Path(tmp_path).exists():
                    Path(tmp_path).unlink()
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.success(f"✅ 成功导入 {success_count}/{len(uploaded_files)} 篇论文")
