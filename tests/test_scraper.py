"""
Test script for PDF scraper to verify section extraction quality.
Tests whether sections are extracted from headings (not inline text).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.ingestion.pdf_scraper import extract_pdf_text


def test_section_extraction(pdf_path: str):
    """
    Test whether PDF scraper correctly extracts sections from headings only.
    """
    print("\n" + "="*80)
    print(f"Testing PDF Scraper: {Path(pdf_path).name}")
    print("="*80 + "\n")
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    # Extract sections
    result = extract_pdf_text(pdf_path)
    
    if result["title"].startswith("ERROR"):
        print(f"❌ Extraction failed: {result['title']}")
        return
    
    print(f"📄 Title: {result['title']}")
    print(f"📝 Full Text Length: {len(result['text'])} characters\n")
    
    sections = result["sections"]
    sections_found = sum([1 for s in sections.values() if s])
    
    print(f"✓ Sections Found: {sections_found}/3\n")
    print("-"*80)
    
    # Test Abstract
    if sections["abstract"]:
        abstract_len = len(sections["abstract"])
        print(f"ABSTRACT: ✓ Found ({abstract_len} chars)")
        print(f"Preview: {sections['abstract'][:200]}...")
        
        # Quality check: Should not be too long
        if abstract_len > 2000:
            print(f"⚠️  WARNING: Abstract is very long ({abstract_len} chars)")
            print("   This might indicate it's grabbing content beyond the abstract section")
        else:
            print(f"✓ Length looks reasonable")
    else:
        print("ABSTRACT: ✗ Not found")
    
    print("\n" + "-"*80)
    
    # Test Introduction
    if sections["introduction"]:
        intro_len = len(sections["introduction"])
        print(f"INTRODUCTION: ✓ Found ({intro_len} chars)")
        print(f"Preview: {sections['introduction'][:200]}...")
        
        # Quality check: Should be substantial but not entire paper
        if intro_len > 10000:
            print(f"⚠️  WARNING: Introduction is very long ({intro_len} chars)")
            print("   This might indicate it's grabbing content beyond the introduction section")
        elif intro_len < 100:
            print(f"⚠️  WARNING: Introduction is very short ({intro_len} chars)")
        else:
            print(f"✓ Length looks reasonable")
    else:
        print("INTRODUCTION: ✗ Not found")
    
    print("\n" + "-"*80)
    
    # Test Conclusion
    if sections["conclusion"]:
        conclusion_len = len(sections["conclusion"])
        print(f"CONCLUSION: ✓ Found ({conclusion_len} chars)")
        print(f"Preview: {sections['conclusion'][:200]}...")
        
        # Quality check: Should not be too long
        if conclusion_len > 5000:
            print(f"⚠️  WARNING: Conclusion is very long ({conclusion_len} chars)")
            print("   This might indicate it's grabbing content beyond the conclusion section")
        else:
            print(f"✓ Length looks reasonable")
    else:
        print("CONCLUSION: ✗ Not found")
    
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    # Calculate if extraction looks accurate
    total_extracted = sum([len(s) for s in sections.values() if s])
    full_text_len = len(result["text"])
    
    extraction_ratio = (total_extracted / full_text_len * 100) if full_text_len > 0 else 0
    
    print(f"Total Extracted: {total_extracted} chars")
    print(f"Full Text: {full_text_len} chars")
    print(f"Extraction Ratio: {extraction_ratio:.1f}%")
    
    if extraction_ratio > 80:
        print("\n❌ PROBLEM DETECTED: Extracting >80% of document")
        print("   This suggests the scraper is NOT identifying section boundaries correctly.")
        print("   It's likely matching keywords anywhere in text, not just as headings.")
        print("\n💡 RECOMMENDATION: Use the experimental scraper (pdf_scraper_experimental.py)")
        print("   which correctly identifies section headings only.")
    elif extraction_ratio > 50:
        print("\n⚠️  WARNING: Extracting >50% of document")
        print("   Some sections may have incorrect boundaries.")
        print("   Check if conclusion includes content from other sections.")
    else:
        print("\n✓ Extraction ratio looks reasonable")
        print("   Sections appear to be correctly bounded.")

def main():
    """Run tests on available PDFs."""
    
    print("\n" + "="*80)
    print("PDF SCRAPER SECTION EXTRACTION TEST")
    print("="*80)
    
    # Test specific PDF directly
    pdf_path = "data_storage/raw_pdfs/sample_paper4.pdf"
    
    if Path(pdf_path).exists():
        test_section_extraction(pdf_path)
    else:
        # Fallback: find any PDF in directory
        pdf_dir = Path("data_storage/raw_pdfs")
        
        if not pdf_dir.exists():
            print(f"\n❌ Directory not found: {pdf_dir}")
            return
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"\n❌ No PDF files found in {pdf_dir}")
            return
        
        print(f"\nFound {len(pdf_files)} PDF file(s), testing first one\n")
        test_section_extraction(str(pdf_files[0]))


if __name__ == "__main__":
    main()
