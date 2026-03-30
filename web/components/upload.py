import streamlit as st
from pathlib import Path

from config import settings
from src.parsers import ParserFactory, TextChunker

PARSER_OPTIONS = {
    "auto": "自动选择（优先 Marker，其次 MinerU，最后 PyMuPDF）",
    "marker": "Marker（版面/标题层级通常比 PyMuPDF 更好）",
    "mineru": "MinerU（对复杂版面更强，但依赖更重）",
    "pymupdf": "PyMuPDF（最快、最稳，但结构还原较弱）",
}


def _parse_with_fallback(pdf_path: str, parser_type: str):
    errors = []

    for candidate in ParserFactory.resolve_parser_order(parser_type):
        try:
            parser = ParserFactory.create_parser(candidate, use_gpu=settings.USE_GPU)
            parsed = parser.parse(pdf_path)
            return parsed, candidate
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")

    raise RuntimeError(" ; ".join(errors))


def render_upload_page():
    st.header("📤 上传论文")

    st.markdown(
        """
        上传 PDF 论文文件，系统会完成解析、入库和向量索引。

        如果 `PyMuPDF` 的结构还原效果不够好，可以优先尝试 `auto`、`Marker` 或 `MinerU`。
        """
    )

    parser_type = st.selectbox(
        "选择解析器",
        list(PARSER_OPTIONS.keys()),
        index=0,
        format_func=lambda key: PARSER_OPTIONS[key],
        help="推荐先用 auto，让系统自动回退到可用解析器",
    )

    st.caption(f"当前选择: `{parser_type}`")

    st.checkbox(
        "使用LLM提取元数据",
        value=False,
        disabled=True,
        help="LLM 元数据增强链路暂未恢复到稳定状态",
    )

    uploaded_files = st.file_uploader(
        "选择PDF文件",
        type=["pdf"],
        accept_multiple_files=True,
        help="支持批量上传，建议每次不超过10篇",
    )

    if uploaded_files and st.button("开始导入", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0

        for i, uploaded_file in enumerate(uploaded_files):
            unparsed_path = None
            try:
                status_text.text(f"正在处理: {uploaded_file.name}")

                unparsed_dir = Path(settings.PDF_DIR) / "unparsed"
                parsed_dir = Path(settings.PDF_DIR) / "parsed"
                unparsed_dir.mkdir(parents=True, exist_ok=True)
                parsed_dir.mkdir(parents=True, exist_ok=True)

                unparsed_path = unparsed_dir / uploaded_file.name
                if unparsed_path.exists():
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{unparsed_path.stem}_{timestamp}.pdf"
                    unparsed_path = unparsed_dir / filename
                else:
                    filename = uploaded_file.name

                unparsed_path.write_bytes(uploaded_file.read())

                parsed, actual_parser = _parse_with_fallback(str(unparsed_path), parser_type)

                parsed_path = parsed_dir / filename
                unparsed_path.rename(parsed_path)

                paper_id = st.session_state.sql_manager.add_paper(
                    title=parsed.title,
                    pdf_path=str(parsed_path),
                    authors=", ".join(parsed.authors)
                    if isinstance(parsed.authors, list)
                    else parsed.authors,
                    abstract=parsed.abstract,
                    raw_text=parsed.full_text,
                    markdown_text=parsed.markdown_text,
                )

                chunker = TextChunker(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                chunks = chunker.chunk_text(
                    parsed.full_text,
                    {"paper_id": paper_id, "title": parsed.title},
                )

                if chunks:
                    chunk_texts = [chunk["text"] for chunk in chunks]
                    chunk_metadatas = [chunk.get("metadata", {}) for chunk in chunks]
                    st.session_state.vector_manager.add_fulltext(
                        paper_id, chunk_texts, chunk_metadatas
                    )

                if parsed.abstract:
                    st.session_state.vector_manager.add_abstract(
                        paper_id,
                        parsed.abstract,
                        {"paper_id": paper_id, "title": parsed.title},
                    )

                success_count += 1
                st.success(f"✓ {uploaded_file.name}（解析器: {actual_parser}）")
            except Exception as exc:
                st.error(f"处理 {uploaded_file.name} 失败: {exc}")
            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.empty()

        if success_count == len(uploaded_files):
            st.success(f"✅ 全部导入成功！共 {success_count} 篇论文")
            st.balloons()
        elif success_count > 0:
            st.warning(f"⚠ 部分导入成功: {success_count}/{len(uploaded_files)} 篇论文")
        else:
            st.error("❌ 导入失败，请检查错误信息")
