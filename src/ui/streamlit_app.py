import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# --- Import pipeline functions ---
from src.groq_rag_pipeline import answer_query
from src.data.data_ingest_pipeline import ingest_pdf_file, ingest_url
from src.config.paths import RAW_PDFS

# Optional: refresh function for Chroma
_refresh_fn = None
try:
    from src.data.vectorstore.chroma_client import refresh_client_and_collection as _refresh_fn
except Exception:
    try:
        from src.data.vectorstore.chroma_client import refresh_client as _refresh_fn
    except Exception:
        _refresh_fn = None

# Initialize session state
if 'ingesting' not in st.session_state:
    st.session_state['ingesting'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# Page config & header
st.set_page_config(page_title="Groq RAG — Demo", layout="wide", initial_sidebar_state="expanded")
st.markdown("<h1 style='margin-bottom: 0.1rem;'>Groq RAG Pipeline</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color: #555; margin-top: 0;'>Upload PDFs or provide web page URLs to ingest content. "
    "Ask questions about ingested documents — answers are generated using Groq's LLM and retrieved context from ChromaDB.</p>",
    unsafe_allow_html=True,
)
st.divider()

# ------------------ Layout: Left (main) and Right (provenance) ------------------
left_col, right_col = st.columns([3, 1])

# ------------------ Left Column: Ingestion + Query ------------------
with left_col:
    # ---------- Ingestion Section ----------
    with st.container():
        st.markdown("## Ingest Content")
        st.write("Upload PDFs (saved to `raw_pdfs`) or paste one or more webpage URLs (one per line). Each source is processed and indexed for immediate retrieval.")

        # --- PDF ingestion UI ---
        st.markdown("### Upload PDFs")
        uploaded_pdfs = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)
        ingest_pdfs_btn = st.button("Ingest Uploaded PDFs", key="ingest_pdfs", disabled=st.session_state.get('ingesting', False))

        if ingest_pdfs_btn:
            if not uploaded_pdfs:
                st.warning("Please upload at least one PDF.")
            else:
                st.session_state['ingesting'] = True
                pdf_folder = Path(RAW_PDFS)
                pdf_folder.mkdir(parents=True, exist_ok=True)

                stats = {"total": len(uploaded_pdfs), "successful": 0, "failed": 0, "failed_files": []}
                with st.spinner("Saving and ingesting PDFs..."):
                    for i, uploaded_file in enumerate(uploaded_pdfs, start=1):
                        try:
                            save_path = pdf_folder / uploaded_file.name
                            with open(save_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            st.info(f"Saved: {save_path.name}")

                            chunks = ingest_pdf_file(str(save_path))
                            if chunks > 0:
                                st.success(f"[{i}/{len(uploaded_pdfs)}] Ingested {uploaded_file.name} ({chunks} chunks)")
                                stats["successful"] += 1
                            else:
                                st.warning(f"[{i}/{len(uploaded_pdfs)}] No content found in {uploaded_file.name}")
                                stats["failed"] += 1
                                stats["failed_files"].append(uploaded_file.name)

                        except Exception as e:
                            st.error(f"[{i}/{len(uploaded_pdfs)}] Failed to ingest {uploaded_file.name}: {e}")
                            stats["failed"] += 1
                            stats["failed_files"].append(uploaded_file.name)

                    # refresh chroma client/collection if available
                    if _refresh_fn:
                        try:
                            _refresh_fn()
                            st.info("🔄 Chroma client refreshed successfully.")
                        except Exception as e:
                            st.warning(f"Could not refresh Chroma client: {e}")

                st.session_state['ingesting'] = False

                # Summary
                st.markdown("**Ingestion Summary**")
                st.write(f"✅ Successful: {stats['successful']} / {stats['total']}")
                if stats["failed_files"]:
                    st.write("❌ Failed files:")
                    for f in stats["failed_files"]:
                        st.write(f"- {f}")

        st.markdown("---")

        # --- Multi-URL ingestion UI ---
        st.markdown("### Ingest Web Pages (multiple URLs)")
        st.write("Paste one or more webpage URLs (one per line). Each URL will be fetched and ingested individually.")
        url_input = st.text_area("Enter URLs (one per line):", height=120, placeholder="https://example.com\nhttps://another-site.org")
        ingest_urls_btn = st.button("Ingest URLs", key="ingest_urls", disabled=st.session_state.get('ingesting', False))

        if ingest_urls_btn:
            urls = [u.strip() for u in url_input.splitlines() if u.strip()]
            if not urls:
                st.warning("Please enter at least one valid URL.")
            else:
                st.session_state['ingesting'] = True
                total = len(urls)
                success_count = 0
                failed_urls = []

                with st.spinner(f"Ingesting {total} URLs..."):
                    for i, url in enumerate(urls, start=1):
                        st.write(f"🌐 Processing [{i}/{total}]: {url}")
                        try:
                            chunks = ingest_url(url)
                            if chunks > 0:
                                st.success(f"✅ Ingested {url} into {chunks} chunks.")
                                success_count += 1
                            else:
                                st.warning(f"⚠️ No extractable content found at {url}.")
                                failed_urls.append(url)
                        except Exception as e:
                            st.error(f"❌ Failed to ingest {url}: {e}")
                            failed_urls.append(url)

                    # Refresh Chroma after ingestion
                    if _refresh_fn:
                        try:
                            _refresh_fn()
                            st.info("🔄 Chroma client refreshed successfully after URL ingestion.")
                        except Exception as e:
                            st.warning(f"Could not refresh Chroma client: {e}")

                st.session_state['ingesting'] = False

                # Summary
                st.markdown("**Ingestion Summary**")
                st.write(f"✅ Successful: {success_count} / {total}")
                if failed_urls:
                    st.write("❌ Failed URLs:")
                    for f in failed_urls:
                        st.write(f"- {f}")

    st.divider()

    # ---------- Query Section ----------
    with st.container():
        st.markdown("## Ask a Question")
        user_question = st.text_input("Enter your question:", key="user_question")

        get_answer_btn = st.button("Get Answer", key="get_answer", disabled=st.session_state.get('ingesting', False))

        if get_answer_btn:
            if not user_question.strip():
                st.warning("Please enter a question!")
            else:
                with st.spinner("Generating answer..."):
                    try:
                        result = answer_query(user_question, n_results=5)
                        # store last_result for right column to display
                        st.session_state['last_result'] = result
                    except Exception as e:
                        st.error(f"Error while generating answer: {e}")
                        st.session_state['last_result'] = None

                # Display answer on success
                if st.session_state['last_result']:
                    res = st.session_state['last_result']
                    st.markdown("### Answer")
                    st.success(res.get("answer", "No answer returned."))

                    # show context stats and optional view of context
                    context = res.get("context", "") or ""
                    context_chars = len(context)
                    est_tokens = context_chars // 4
                    st.caption(f"Context size: {context_chars} chars (~{est_tokens} tokens)")

                    with st.expander("Show retrieved context (debug view)", expanded=False):
                        st.code(context[:8000] + ("... [truncated]" if len(context) > 8000 else ""), language="text")

# ------------------ Right Column: Provenance & Stats ------------------
with right_col:
    st.markdown("## Retrieval Stats & Sources")
    st.write("Provenance for the latest answer is shown below. Expand any document to see a snippet and metadata.")

    result = st.session_state.get('last_result', None)
    if result:
        docs = result.get("retrieved_docs", []) or []
        # compute avg similarity if present
        similarities = [d.get("similarity") for d in docs if d.get("similarity") is not None]
        avg_sim = sum(similarities) / len(similarities) if similarities else None

        # Metrics row
        m1, m2, m3 = st.columns([1, 1, 1])
        m1.metric("Documents", len(docs))
        m2.metric("Avg Similarity", f"{avg_sim:.3f}" if avg_sim is not None else "N/A")
        m3.metric("Context chars", len(result.get("context", "") or ""))

        st.markdown("---")

        if docs:
            # Build overview table
            table_rows = []
            for d in docs:
                table_rows.append({
                    "Doc #": d.get("doc_index"),
                    "Source": d.get("source"),
                    "Section": d.get("section"),
                    "Similarity": f"{d.get('similarity'):.3f}" if d.get('similarity') is not None else "N/A",
                    "Len": d.get("full_text_length", "N/A")
                })
            df = pd.DataFrame(table_rows)
            st.dataframe(df, use_container_width=True)

            st.markdown("### Document previews")
            for d in docs:
                doc_header = f"Document {d.get('doc_index')} — {d.get('source')} (Section: {d.get('section')})"
                with st.expander(doc_header):
                    snippet = d.get("snippet", "")
                    st.write(snippet)
                    st.markdown(f"- **Similarity:** {d.get('similarity'):.3f}" if d.get('similarity') is not None else "- **Similarity:** N/A")
                    st.markdown(f"- **Chunk index:** {d.get('chunk_index')}")
                    st.markdown(f"- **Distance:** {d.get('distance')}")
        else:
            st.info("No retrieved documents returned for the latest query.")
    else:
        st.info("No query executed yet. Ingest documents or URLs and ask a question to see results.")

# ------------------ Footer / Tips ------------------
st.divider()
st.caption(
    "Tips: 1) Upload PDFs or ingest URLs before querying.  2) If results are missing, try a broader query or re-ingest the source. "
    "3) For production, restrict uploads and secure API keys."
)





