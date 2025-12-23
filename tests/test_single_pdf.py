"""
Quick test script for experimental PDF scraper
Usage: python test_single_pdf.py path/to/paper.pdf
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.ingestion import pdf_scraper_experimental


def test_single_pdf(pdf_path: str):
    """Test experimental scraper on a single PDF."""
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    print("\n" + "="*80)
    print(f"Testing: {Path(pdf_path).name}")
    print("="*80 + "\n")
    
    try:
        # Extract sections
        result = pdf_scraper_experimental.extract_pdf_text(pdf_path)
        
        # Display results
        print(f"📄 Title: {result['title']}")
        print(f"📖 Pages: {result['metadata']['pages']}")
        print(f"🔍 Extraction Method: {result['metadata']['extraction_method']}")
        print(f"✓ Sections Found: {', '.join(result['metadata']['sections_found']) if result['metadata']['sections_found'] else 'None'}")
        print()
        
        # Show quality assessment
        sections_found = len(result['metadata']['sections_found'])
        print("Quality Assessment:")
        if sections_found == 3:
            print("  ✓✓✓ EXCELLENT - All 3 sections extracted!")
        elif sections_found == 2:
            print("  ✓✓ GOOD - 2 sections extracted")
        elif sections_found == 1:
            print("  ✓ FAIR - 1 section extracted")
        else:
            print("  ✗ POOR - No sections found")
        print()
        
        # Display each section
        sections = result['sections']
        
        if sections['abstract']:
            print("-"*80)
            print("ABSTRACT")
            print("-"*80)
            print(sections['abstract'][:500] + "..." if len(sections['abstract']) > 500 else sections['abstract'])
            print(f"\n[Full length: {len(sections['abstract'])} characters]\n")
        else:
            print("-"*80)
            print("ABSTRACT: Not found ❌")
            print("-"*80 + "\n")
        
        if sections['introduction']:
            print("-"*80)
            print("INTRODUCTION")
            print("-"*80)
            print(sections['introduction'][:700] + "..." if len(sections['introduction']) > 700 else sections['introduction'])
            print(f"\n[Full length: {len(sections['introduction'])} characters]\n")
        else:
            print("-"*80)
            print("INTRODUCTION: Not found ❌")
            print("-"*80 + "\n")
        
        if sections['conclusion']:
            print("-"*80)
            print("CONCLUSION")
            print("-"*80)
            print(sections['conclusion'][:500] + "..." if len(sections['conclusion']) > 500 else sections['conclusion'])
            print(f"\n[Full length: {len(sections['conclusion'])} characters]\n")
        else:
            print("-"*80)
            print("CONCLUSION: Not found ❌")
            print("-"*80 + "\n")
        
        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Extraction Method: {result['metadata']['extraction_method']}")
        print(f"Sections Found: {sections_found}/3")
        print(f"Total Text Length: {len(result['text'])} characters")
        
        # Recommendations
        print("\nRecommendations:")
        if sections_found >= 2:
            print("  ✓ This scraper works well for this PDF format")
            print("  ✓ Consider using experimental scraper for similar papers")
        elif sections_found == 1:
            print("  ⚠️  Partial extraction - check paper formatting")
            print("  ⚠️  May need manual review or pattern adjustments")
        else:
            print("  ❌ Poor extraction - possible reasons:")
            print("     - Non-standard formatting")
            print("     - Scanned/image-based PDF")
            print("     - Sections have different names")
            print("  💡 Try viewing the PDF to check structure")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function."""
    
    print("\n" + "="*80)
    print("EXPERIMENTAL PDF SCRAPER - QUICK TEST")
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\nUsage: python test_single_pdf.py path/to/paper.pdf")
        print("\nNo path provided. Looking for PDFs in data_storage/raw_pdfs/...\n")
        
        pdf_dir = Path("data_storage/raw_pdfs")
        if pdf_dir.exists():
            pdf_files = list(pdf_dir.glob("*.pdf"))
            if pdf_files:
                print(f"Found {len(pdf_files)} PDF(s):")
                for i, pdf in enumerate(pdf_files, 1):
                    print(f"  {i}. {pdf.name}")
                
                if len(pdf_files) == 1:
                    print(f"\nTesting the only PDF found...")
                    test_single_pdf(str(pdf_files[0]))
                else:
                    choice = input(f"\nSelect PDF (1-{len(pdf_files)}): ").strip()
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(pdf_files):
                            test_single_pdf(str(pdf_files[idx]))
                        else:
                            print("Invalid selection")
                    except ValueError:
                        print("Invalid input")
            else:
                print("No PDFs found. Please provide a path:")
                print("python test_single_pdf.py path/to/paper.pdf")
        else:
            print(f"Directory not found: {pdf_dir}")
            print("\nPlease provide a PDF path:")
            print("python test_single_pdf.py path/to/paper.pdf")
    else:
        pdf_path = sys.argv[1]
        test_single_pdf(pdf_path)
    
    print()


if __name__ == "__main__":
    main()
