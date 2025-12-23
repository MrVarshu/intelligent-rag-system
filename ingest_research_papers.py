"""
Research Paper Ingestion Script
Specialized script for ingesting academic research papers into ChromaDB.
Optimized for papers with Abstract, Introduction, and Conclusion sections.
"""

from pathlib import Path
from src.data.data_ingest_pipeline import ingest_pdf_file
from src.config.paths import RAW_PDFS
from src.data.vectorstore.chroma_client import collection
from src.data.ingestion.pdf_scraper import extract_pdf_text


def analyze_paper_structure(pdf_path):
    """
    Analyze the structure of a research paper.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with section information
    """
    result = extract_pdf_text(pdf_path)
    
    if result.get("error"):
        return {"error": result["error"]}
    
    sections = result.get("sections", {})
    
    analysis = {
        "title": result.get("title", "Unknown"),
        "has_abstract": bool(sections.get("abstract")),
        "has_introduction": bool(sections.get("introduction")),
        "has_conclusion": bool(sections.get("conclusion")),
        "abstract_length": len(sections.get("abstract", "")),
        "introduction_length": len(sections.get("introduction", "")),
        "conclusion_length": len(sections.get("conclusion", "")),
    }
    
    analysis["total_content_length"] = (
        analysis["abstract_length"] + 
        analysis["introduction_length"] + 
        analysis["conclusion_length"]
    )
    
    return analysis


def ingest_research_papers(pdf_folder=None, max_chunk_size=1500, analyze_first=True):
    """
    Ingest research papers with structure analysis.
    
    Args:
        pdf_folder: Path to folder containing research papers (default: RAW_PDFS)
        max_chunk_size: Maximum characters per chunk (default: 1500)
        analyze_first: Whether to analyze paper structure before ingestion
    
    Returns:
        Dictionary with ingestion statistics
    """
    print("="*80)
    print("RESEARCH PAPER INGESTION SCRIPT")
    print("="*80)
    
    # Use default folder if not specified
    if pdf_folder is None:
        pdf_folder = Path(RAW_PDFS)
    else:
        pdf_folder = Path(pdf_folder)
    
    # Check if folder exists
    if not pdf_folder.exists():
        print(f"❌ Folder not found: {pdf_folder}")
        print(f"\nPlease create the folder and add research papers:")
        print(f"  mkdir -p {pdf_folder}")
        return {"error": "Folder not found"}
    
    # Get all PDF files
    pdf_files = list(pdf_folder.glob('*.pdf'))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in: {pdf_folder}")
        print(f"\nPlease add research paper PDFs to the folder.")
        return {"error": "No PDFs found"}
    
    print(f"\n📁 Folder: {pdf_folder}")
    print(f"📄 Found {len(pdf_files)} research paper(s) to ingest\n")
    
    # Track statistics
    stats = {
        "total_files": len(pdf_files),
        "successful": 0,
        "failed": 0,
        "total_chunks": 0,
        "papers_with_abstract": 0,
        "papers_with_introduction": 0,
        "papers_with_conclusion": 0,
        "failed_files": [],
        "paper_details": []
    }
    
    # Process each paper
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
        print(f"{'='*80}")
        
        paper_info = {
            "filename": pdf_path.name,
            "path": str(pdf_path)
        }
        
        try:
            # Analyze structure if requested
            if analyze_first:
                print("📊 Analyzing paper structure...")
                analysis = analyze_paper_structure(str(pdf_path))
                
                if analysis.get("error"):
                    raise Exception(f"Analysis failed: {analysis['error']}")
                
                paper_info.update(analysis)
                
                print(f"  📑 Title: {analysis['title']}")
                print(f"  📄 Sections found:")
                print(f"     Abstract: {'✅' if analysis['has_abstract'] else '❌'} ({analysis['abstract_length']} chars)")
                print(f"     Introduction: {'✅' if analysis['has_introduction'] else '❌'} ({analysis['introduction_length']} chars)")
                print(f"     Conclusion: {'✅' if analysis['has_conclusion'] else '❌'} ({analysis['conclusion_length']} chars)")
                print(f"  📏 Total content: {analysis['total_content_length']} characters")
                
                # Track section statistics
                if analysis['has_abstract']:
                    stats['papers_with_abstract'] += 1
                if analysis['has_introduction']:
                    stats['papers_with_introduction'] += 1
                if analysis['has_conclusion']:
                    stats['papers_with_conclusion'] += 1
                
                # Warn if no sections found
                if analysis['total_content_length'] == 0:
                    print("  ⚠️  Warning: No key sections found in this paper!")
            
            # Ingest the paper
            print(f"\n🔄 Ingesting paper into ChromaDB...")
            n_chunks = ingest_pdf_file(str(pdf_path), max_chars=max_chunk_size)
            
            paper_info["chunks"] = n_chunks
            
            if n_chunks > 0:
                print(f"  ✅ Successfully ingested {n_chunks} chunks")
                stats["successful"] += 1
                stats["total_chunks"] += n_chunks
            else:
                print(f"  ⚠️  No content extracted (0 chunks)")
                stats["failed"] += 1
                stats["failed_files"].append({
                    "file": pdf_path.name,
                    "reason": "No content extracted"
                })
                paper_info["status"] = "failed"
                
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            stats["failed"] += 1
            stats["failed_files"].append({
                "file": pdf_path.name,
                "reason": str(e)
            })
            paper_info["status"] = "failed"
            paper_info["error"] = str(e)
        
        stats["paper_details"].append(paper_info)
    
    # Print detailed summary
    print("\n" + "="*80)
    print("RESEARCH PAPER INGESTION SUMMARY")
    print("="*80)
    print(f"\n📊 Overall Statistics:")
    print(f"  Total papers processed:    {stats['total_files']}")
    print(f"  ✅ Successfully ingested:  {stats['successful']}")
    print(f"  ❌ Failed:                 {stats['failed']}")
    print(f"  📦 Total chunks created:   {stats['total_chunks']}")
    
    if analyze_first:
        print(f"\n📑 Section Coverage:")
        print(f"  Papers with Abstract:      {stats['papers_with_abstract']}/{stats['total_files']}")
        print(f"  Papers with Introduction:  {stats['papers_with_introduction']}/{stats['total_files']}")
        print(f"  Papers with Conclusion:    {stats['papers_with_conclusion']}/{stats['total_files']}")
    
    if stats["failed_files"]:
        print(f"\n⚠️  Failed Papers:")
        for fail in stats["failed_files"]:
            print(f"  ❌ {fail['file']}")
            print(f"     Reason: {fail['reason']}")
    
    # Show successful papers
    if stats["successful"] > 0:
        print(f"\n✅ Successfully Ingested Papers:")
        for paper in stats["paper_details"]:
            if paper.get("status") != "failed":
                chunks = paper.get("chunks", 0)
                print(f"  • {paper['filename']}: {chunks} chunks")
    
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
    Main function to run research paper ingestion.
    """
    print("\n" + "="*80)
    print("RESEARCH PAPER INGESTION FOR RAG SYSTEM")
    print("="*80)
    print("\nThis script is optimized for academic research papers.")
    print("It extracts Abstract, Introduction, and Conclusion sections.")
    
    # Configuration options
    print(f"\n📋 Configuration Options:")
    print(f"  Default folder: {RAW_PDFS}")
    
    custom_folder = input("\nEnter custom folder path (or press Enter to use default): ").strip()
    folder = custom_folder if custom_folder else None
    
    print(f"\n  Default chunk size: 1500 characters")
    custom_size = input("Enter custom chunk size (or press Enter to use default): ").strip()
    chunk_size = int(custom_size) if custom_size.isdigit() else 1500
    
    analyze = input("\nAnalyze paper structure before ingestion? (y/n, default: y): ").strip().lower()
    analyze_first = analyze != 'n'
    
    # Confirm configuration
    print(f"\n📋 Final Configuration:")
    print(f"  Folder: {folder or RAW_PDFS}")
    print(f"  Chunk size: {chunk_size} characters")
    print(f"  Structure analysis: {'Enabled' if analyze_first else 'Disabled'}")
    
    proceed = input("\nProceed with ingestion? (y/n): ").strip().lower()
    
    if proceed != 'y':
        print("\n❌ Ingestion cancelled.")
        return
    
    # Run ingestion
    stats = ingest_research_papers(
        pdf_folder=folder,
        max_chunk_size=chunk_size,
        analyze_first=analyze_first
    )
    
    # Final message
    if stats.get("error"):
        print(f"\n❌ Ingestion failed: {stats['error']}")
    elif stats["successful"] > 0:
        print(f"\n✅ Research paper ingestion complete!")
        print(f"\n📚 {stats['successful']} paper(s) successfully ingested")
        print(f"📦 {stats['total_chunks']} total chunks created")
        
        print(f"\n🚀 You can now query your RAG system:")
        print(f"  • Streamlit: streamlit run src/ui/streamlit_app.py")
        print(f"  • Interactive: python interactive_groq_rag.py")
        
        print(f"\n💡 Example queries:")
        print(f"  • 'Summarize the abstract of the papers'")
        print(f"  • 'What are the main conclusions?'")
        print(f"  • 'Explain the key concepts from the introduction'")
    else:
        print(f"\n⚠️  No papers were successfully ingested.")
        print(f"Please check your PDF files and try again.")


if __name__ == "__main__":
    main()
