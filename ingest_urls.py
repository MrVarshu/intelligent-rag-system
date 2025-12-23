"""
URL Ingestion Script
Ingest web pages from URLs into ChromaDB.
This script fetches, cleans, chunks, and stores web content.
"""

from src.data.data_ingest_pipeline import ingest_url
from src.data.vectorstore.chroma_client import collection


def ingest_multiple_urls(urls):
    """
    Ingest content from multiple URLs.
    
    Args:
        urls: List of URL strings to ingest
    
    Returns:
        Dictionary with ingestion statistics
    """
    print("="*80)
    print("URL INGESTION SCRIPT")
    print("="*80)
    
    if not urls:
        print("⚠️  No URLs provided")
        print("\nPlease add URLs to the urls_to_ingest list in this script.")
        return {"error": "No URLs provided"}
    
    print(f"\n🌐 Found {len(urls)} URL(s) to ingest\n")
    
    # Track statistics
    stats = {
        "total_urls": len(urls),
        "successful": 0,
        "failed": 0,
        "total_chunks": 0,
        "failed_urls": []
    }
    
    # Process each URL
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] Processing: {url}")
        
        try:
            # Ingest the URL
            n_chunks = ingest_url(url)
            
            if n_chunks > 0:
                print(f"  ✅ Successfully ingested {n_chunks} chunks")
                stats["successful"] += 1
                stats["total_chunks"] += n_chunks
            else:
                print(f"  ⚠️  No content extracted (0 chunks)")
                stats["failed"] += 1
                stats["failed_urls"].append({
                    "url": url,
                    "reason": "No content extracted"
                })
                
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            stats["failed"] += 1
            stats["failed_urls"].append({
                "url": url,
                "reason": str(e)
            })
    
    # Print summary
    print("\n" + "="*80)
    print("INGESTION SUMMARY")
    print("="*80)
    print(f"Total URLs processed:   {stats['total_urls']}")
    print(f"  ✅ Successful:        {stats['successful']}")
    print(f"  ❌ Failed:            {stats['failed']}")
    print(f"  📦 Total chunks:      {stats['total_chunks']}")
    
    if stats["failed_urls"]:
        print(f"\n⚠️  Failed URLs:")
        for fail in stats["failed_urls"]:
            print(f"  ❌ {fail['url']}")
            print(f"     Reason: {fail['reason']}")
    
    # Show ChromaDB status
    try:
        total_docs = collection.count()
        print(f"\n📊 Total documents in ChromaDB: {total_docs}")
    except Exception as e:
        print(f"\n⚠️  Could not get ChromaDB count: {e}")
    
    print("="*80)
    
    return stats


def main():
    """
    Main function to run URL ingestion.
    """
    print("\n" + "="*80)
    print("WEB CONTENT INGESTION FOR RAG SYSTEM")
    print("="*80)
    
    # ===================================================================
    # CONFIGURE YOUR URLs HERE
    # ===================================================================
    urls_to_ingest = [
        # Wikipedia AI/ML Articles
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning",
        "https://en.wikipedia.org/wiki/Natural_language_processing",
        
        # Add more URLs below:
        # "https://example.com/article1",
        # "https://example.com/blog-post",
        # "https://docs.example.com/documentation",
    ]
    # ===================================================================
    
    if not urls_to_ingest:
        print("\n⚠️  No URLs configured!")
        print("\nPlease edit this script and add URLs to the 'urls_to_ingest' list.")
        return
    
    print(f"\n📋 Configuration:")
    print(f"  URLs to ingest: {len(urls_to_ingest)}")
    
    # Show URLs
    print(f"\n🌐 URLs:")
    for idx, url in enumerate(urls_to_ingest, 1):
        print(f"  {idx}. {url}")
    
    # Run ingestion
    print("\n" + "="*80)
    stats = ingest_multiple_urls(urls_to_ingest)
    
    # Final message
    if stats.get("error"):
        print(f"\n❌ Ingestion failed: {stats['error']}")
    elif stats["successful"] > 0:
        print(f"\n✅ URL ingestion complete!")
        print(f"\n🌐 {stats['successful']} URL(s) successfully ingested")
        print(f"📦 {stats['total_chunks']} total chunks created")
        
        print(f"\n🚀 You can now query your RAG system:")
        print(f"  • Streamlit: streamlit run src/ui/streamlit_app.py")
        print(f"  • Interactive: python interactive_groq_rag.py")
        
        print(f"\n💡 Example queries:")
        print(f"  • 'What is artificial intelligence?'")
        print(f"  • 'Explain machine learning concepts'")
        print(f"  • 'Summarize the key points from the articles'")
    else:
        print(f"\n⚠️  No URLs were successfully ingested.")
        print(f"Please check your URLs and internet connection, then try again.")


if __name__ == "__main__":
    main()
