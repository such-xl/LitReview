import streamlit as st
from pathlib import Path
import tempfile
from src.parsers import ParserFactory, TextChunker
from src.llm import LLMFactory
from config import settings

def render_upload_page():
    st.header("📤 上传论文")
    
    st.markdown("""
    上传PDF论文文件，系统将自动解析并创建索引。
    
    💡 **提示**: 如果使用LLM提取，请确保侧边栏中的LLM服务已配置并运行。
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        parser_type = st.selectbox(
            "选择解析器", 
            ["mineru"],
            help="MinerU: 高质量GPU加速"
        )
    
    with col2:
        use_llm = st.checkbox("使用LLM提取元数据", value=True, help="智能提取标题、作者、摘要等（需要LLM服务运行）")
    
    use_gpu = False
    if parser_type == "mineru":
        use_gpu = st.checkbox("使用GPU加速", value=True, help="需要CUDA环境")
    
    uploaded_files = st.file_uploader(
        "选择PDF文件",
        type=['pdf'],
        accept_multiple_files=True,
        help="支持批量上传，建议每次不超过10篇"
    )
    
    if uploaded_files and st.button("开始导入", type="primary"):
        # 初始化LLM

        
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            unparsed_path = None
            parsed_path = None
            try:
                status_text.text(f"正在处理: {uploaded_file.name}")
                
                # 创建两个目录：未解析和已解析
                unparsed_dir = Path(settings.PDF_DIR) / "unparsed"
                parsed_dir = Path(settings.PDF_DIR) / "parsed"

                unparsed_dir.mkdir(parents=True, exist_ok=True)
                parsed_dir.mkdir(parents=True, exist_ok=True)
                
                
                # 先保存到未解析目录
                unparsed_path = unparsed_dir / uploaded_file.name
                
                # 如果文件已存在，添加时间戳
                if unparsed_path.exists():
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{unparsed_path.stem}_{timestamp}.pdf"
                    unparsed_path = unparsed_dir / filename
                else:
                    filename = uploaded_file.name
                
                unparsed_path.write_bytes(uploaded_file.read())
                
        

                # 创建解析器（MinerU支持LLM）
                # if parser_type == "mineru":
                #     from src.parsers.mineru_chunker import MinerUParser
                #     parser = MinerUParser(use_gpu=use_gpu, llm=llm)
                # else:
                #     parser = ParserFactory.create_parser(parser_type, use_gpu=use_gpu)
                
                # 解析PDF（使用未解析目录的文件）
                # parsed = parser.parse(str(unparsed_path))
                
                # 解析成功后，移动到已解析目录
                # parsed_path = parsed_dir / filename
                # unparsed_path.rename(parsed_path)
                
                # 存入数据库（使用已解析目录的路径）
                # paper_id = st.session_state.sql_manager.add_paper(
                #     title=parsed.title,
                #     pdf_path=str(parsed_path),
                #     authors=', '.join(parsed.authors) if isinstance(parsed.authors, list) else parsed.authors,
                #     raw_text=parsed.full_text,
                #     markdown_text=parsed.markdown_text
                # )
                
                # 向量化存储
                # chunker = TextChunker(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                # chunks = chunker.chunk_text(parsed.full_text, {"paper_id": paper_id})
                
                # if chunks:
                #     chunk_texts = [chunk["text"] for chunk in chunks]
                #     st.session_state.vector_manager.add_fulltext(paper_id, chunk_texts)
                
                success_count += 1
                st.success(f"✓ {uploaded_file.name}")
                
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg:
                    st.error(f"处理 {uploaded_file.name} 失败: LLM服务不可用")
                else:
                    st.error(f"处理 {uploaded_file.name} 失败: {error_msg}")
                    # 如果处理失败，PDF保留在unparsed目录
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.empty()
        
        if success_count == len(uploaded_files):
            st.success(f"✅ 全部导入成功！共 {success_count} 篇论文")
            st.balloons()
        elif success_count > 0:
            st.warning(f"⚠ 部分导入成功: {success_count}/{len(uploaded_files)} 篇论文")
        else:
            st.error("❌ 导入失败，请检查错误信息")
