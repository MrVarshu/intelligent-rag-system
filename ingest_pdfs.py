from pathlib import Path
from src.data.data_ingest_pipeline import ingest_pdf_file
from src.config.paths import RAW_PDFS
from src.data.vectorstore.chroma_client import collection
import shutil


def ingest_all_pdfs(uploaded_files=None, max_chunk_size=1500):
    """
    Ingest uploaded PDF files into ChromaDB after saving them to RAW_PDFS folder.

    Args:
        uploaded_files: List of uploaded file objects (e.g., Streamlit UploadedFile)
        max_chunk_size: Maximum characters per chunk

    Returns:
        Dictionary with ingestion statistics
    """
    print("="*80)
    print("PDF INGESTION SCRIPT")
    print("="*80)

    if not uploaded_files:
        print("❌ No PDF files provided for ingestion.")
        return {"error": "No PDFs provided"}

    # Ensure RAW_PDFS folder exists
    raw_folder = Path(RAW_PDFS)
    raw_folder.mkdir(parents=True, exist_ok=True)

    # Save uploaded files to RAW_PDFS
    pdf_paths = []
    for uploaded_file in uploaded_files:
        dest_path = raw_folder / uploaded_file.name
        with open(dest_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        pdf_paths.append(dest_path)
        print(f"📄 Saved uploaded PDF: {dest_path}")

    # Now ingest only the uploaded PDFs
    stats = {
        "total_files": len(pdf_paths),
        "successful": 0,
        "failed": 0,
        "total_chunks": 0,
        "failed_files": []
    }

    for idx, pdf_path in enumerate(pdf_paths, 1):
        print(f"\n[{idx}/{len(pdf_paths)}] Processing: {pdf_path.name}")
        try:
            n_chunks = ingest_pdf_file(str(pdf_path), max_chars=max_chunk_size)
            if n_chunks > 0:
                print(f"  ✅ Successfully ingested {n_chunks} chunks")
                stats["successful"] += 1
                stats["total_chunks"] += n_chunks
            else:
                print(f"  ⚠️  No content extracted (0 chunks)")
                stats["failed"] += 1
                stats["failed_files"].append({"file": pdf_path.name, "reason": "No content extracted"})
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            stats["failed"] += 1
            stats["failed_files"].append({"file": pdf_path.name, "reason": str(e)})

    # Show ChromaDB status
    try:
        total_docs = collection.count()
        print(f"\n📊 Total documents in ChromaDB: {total_docs}")
    except Exception as e:
        print(f"\n⚠️  Could not get ChromaDB count: {e}")

    print("="*80)
    return stats
