import streamlit as st
from src.llm import LLMFactory
from src.synthesis import LiteratureReviewGenerator, CitationManager
from config import settings

def render_review_page():
    st.header("📝 生成文献综述")
    
    topic = st.text_input("研究主题", placeholder="例如: 深度学习在自然语言处理中的应用")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_papers = st.slider("使用论文数量", 5, 50, 20)
    
    with col2:
        review_type = st.selectbox("综述类型", ["完整综述", "简短摘要"])
    
    if st.button("🚀 生成综述", type="primary"):
        if not topic:
            st.warning("请输入研究主题")
            return
        
        with st.spinner("正在生成综述..."):
            try:
                papers = st.session_state.query_engine.query(
                    topic, method="hybrid", n_results=n_papers
                )
                
                if not papers:
                    st.error("未找到相关论文")
                    return
                
                st.info(f"找到 {len(papers)} 篇相关论文")
                
                # 显示配置信息
                provider = st.session_state.llm_provider
                model = st.session_state.llm_model
                base_url = st.session_state.get('llm_base_url')
                api_key = st.session_state.get('llm_api_key')
                
                with st.expander("🔧 LLM配置"):
                    st.write(f"Provider: {provider}")
                    st.write(f"Model: {model}")
                    st.write(f"Base URL: {base_url}")
                    st.write(f"Has API Key: {bool(api_key)}")
                
                # 验证配置
                if provider == "custom":
                    if not base_url:
                        st.error("⚠️ 请在侧边栏配置中输入 API URL")
                        return
                    if not api_key:
                        st.error("⚠️ 请在侧边栏配置中输入 API Key")
                        return
                    st.info(f"✅ 使用自定义API: {base_url}")
                
                llm = LLMFactory.create_llm(
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    base_url=base_url
                )
                
                generator = LiteratureReviewGenerator(llm, st.session_state.sql_manager)
                
                if review_type == "简短摘要":
                    review_text = generator.generate_summary(papers, topic)
                    st.markdown("### 摘要")
                    st.markdown(review_text)
                else:
                    review_text = generator.generate_review(papers, topic, max_papers=n_papers)
                    st.markdown(f"# {topic} - 文献综述")
                    st.markdown(review_text)
                
                st.markdown("## 参考文献")
                citation_manager = CitationManager()
                for paper in papers:
                    citation_manager.add_citation(paper)
                
                bibliography = citation_manager.generate_bibliography("apa")
                st.markdown(bibliography)
                
                full_text = f"# {topic}\n\n{review_text}\n\n## 参考文献\n\n{bibliography}"
                
                st.download_button(
                    label="📥 下载综述",
                    data=full_text,
                    file_name=f"{topic}_review.md",
                    mime="text/markdown"
                )
                
                st.success("✅ 综述生成完成！")
                
            except Exception as e:
                st.error(f"生成失败: {e}")
                
                # 检查常见问题
                if "Connection" in str(e) or "refused" in str(e):
                    st.error("⚠️ Ollama未运行，请先启动: ollama serve")
                elif "model" in str(e).lower():
                    st.error(f"⚠️ 模型未找到，请先下载: ollama pull {st.session_state.llm_model}")
                
                with st.expander("🐞 查看详细错误"):
                    import traceback
                    st.code(traceback.format_exc())
