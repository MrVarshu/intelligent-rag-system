"""
Bulk Data Ingestion Script
Ingest all PDFs from raw_pdfs folder and multiple URLs into ChromaDB.
"""

from pathlib import Path
from src.data.data_ingest_pipeline import ingest_url, ingest_pdf_file
from src.config.paths import RAW_PDFS

def ingest_all_pdfs():
    """
    Ingest all PDF files from the raw_pdfs folder.
    """
    print("="*80)
    print("INGESTING PDFs FROM raw_pdfs FOLDER")
    print("="*80)
    
    pdf_folder = Path(RAW_PDFS)
    
    # Check if folder exists
    if not pdf_folder.exists():
        print(f"❌ Folder not found: {pdf_folder}")
        print(f"Please create the folder and add PDF files.")
        return 0
    
    # Get all PDF files
    pdf_files = list(pdf_folder.glob('*.pdf'))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in: {pdf_folder}")
        return 0
    
    print(f"\nFound {len(pdf_files)} PDF file(s) to ingest:\n")
    
    total_chunks = 0
    successful = 0
    failed = 0
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
        try:
            n_chunks = ingest_pdf_file(str(pdf_path))
            print(f"  ✓ Ingested {n_chunks} chunks")
            total_chunks += n_chunks
            successful += 1
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"PDF INGESTION COMPLETE")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total chunks ingested: {total_chunks}")
    print("="*80)
    
    return total_chunks


def ingest_multiple_urls(urls):
    """
    Ingest content from multiple URLs.
    
    Args:
        urls: List of URL strings to ingest
    """
    print("\n" + "="*80)
    print("INGESTING URLS")
    print("="*80)
    
    if not urls:
        print("⚠️  No URLs provided")
        return 0
    
    print(f"\nFound {len(urls)} URL(s) to ingest:\n")
    
    total_chunks = 0
    successful = 0
    failed = 0
    
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] Processing: {url}")
        try:
            n_chunks = ingest_url(url)
            print(f"  ✓ Ingested {n_chunks} chunks")
            total_chunks += n_chunks
            successful += 1
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"URL INGESTION COMPLETE")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total chunks ingested: {total_chunks}")
    print("="*80)
    
    return total_chunks


def main():
    """
    Main ingestion script.
    """
    print("\n" + "="*80)
    print("BULK DATA INGESTION FOR RAG SYSTEM")
    print("="*80)
    
    # ===================================================================
    # CONFIGURE YOUR URLs HERE
    # ===================================================================
    urls_to_ingest = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning",
        "https://en.wikipedia.org/wiki/Natural_language_processing",
        # Add more URLs below:
        # "https://example.com/article1",
        # "https://example.com/article2",
    ]
    # ===================================================================
    
    # Step 1: Ingest all PDFs from raw_pdfs folder
    pdf_chunks = ingest_all_pdfs()
    
    # Step 2: Ingest URLs
    url_chunks = ingest_multiple_urls(urls_to_ingest)
    
    # Summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Total PDF chunks ingested: {pdf_chunks}")
    print(f"Total URL chunks ingested: {url_chunks}")
    print(f"Total chunks in ChromaDB: {pdf_chunks + url_chunks}")
    print("="*80)
    
    print("\n✅ Data ingestion complete! You can now query the RAG system.")
    print("\nTo query:")
    print("  • Streamlit: streamlit run src/ui/streamlit_app.py")
    print("  • Interactive: python interactive_groq_rag.py")


if __name__ == "__main__":
    main()
