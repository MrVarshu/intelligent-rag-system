from .ingestion.web_crawler import fetch_url_text
from .ingestion.pdf_scraper import extract_pdf_text
from .ingestion.text_cleaner import clean_text, simple_chunk
from .embedding.embedder import embed_texts
from .vectorstore.chroma_client import add_documents 
from .vectorstore.vector_utils import make_id
from pathlib import Path


def ingest_url(url: str):
    """
    Ingest a web page: fetch, clean, chunk, embed, store in ChromaDB.
    """
    result = fetch_url_text(url)
    text = clean_text(result.get('text', ''))
    chunks = simple_chunk(text)  # returns list[str]
    ids = [make_id(url, i) for i, _ in enumerate(chunks)]
    metadatas = [
        {"source": url, "title": result.get('title', ''), "source_type": "web", "chunk_index": i}
        for i in range(len(chunks))
    ]
    embeddings = embed_texts(chunks) if chunks else []
    add_documents(doc_texts=chunks, metadatas=metadatas, ids=ids, embeddings=embeddings)
    return len(chunks)


def ingest_pdf_file(path: str, max_chars: int = 1500):
    """
    Ingest a PDF file by extracting only Abstract, Introduction, Conclusion.
    Each section is chunked separately, with metadata including section name.
    """
    result = extract_pdf_text(path)
    title = result.get("title", "")
    sections = result.get("sections", {})  # dict with keys: abstract, introduction, conclusion

    all_texts = []
    all_meta = []
    all_ids = []
    total_chunks = 0

    for sec_name in ["abstract", "introduction", "conclusion"]:
        sec_text = clean_text(sections.get(sec_name, ""))
        if not sec_text:
            continue
        chunks = simple_chunk(sec_text, max_chars=max_chars)
        for idx, chunk in enumerate(chunks):
            uid = make_id(f"{path}::{sec_name}", idx)
            meta = {
                "source": path,
                "title": title,
                "section": sec_name,
                "chunk_index": idx
            }
            all_texts.append(chunk)
            all_meta.append(meta)
            all_ids.append(uid)
        total_chunks += len(chunks)

    if all_texts:
        embeddings = embed_texts(all_texts)
        add_documents(doc_texts=all_texts, metadatas=all_meta, ids=all_ids, embeddings=embeddings)
    return total_chunks




