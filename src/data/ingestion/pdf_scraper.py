"""
Experimental PDF Scraper for Research Papers
Improved extraction of Abstract, Introduction, and Conclusion sections
"""

import PyPDF2
import re
from pathlib import Path
from typing import Dict, Optional, List


def extract_pdf_text(pdf_path: str) -> Dict[str, any]:
    """
    Enhanced extraction for research papers with better section detection.
    
    Returns dict:
      {
        "text": "<full_text>",
        "title": "<filename or extracted title>",
        "sections": {
            "abstract": "...",
            "introduction": "...",
            "conclusion": "..."
        },
        "metadata": {
            "pages": int,
            "extraction_method": str,
            "sections_found": List[str]
        }
      }
    """
    text = ""
    pages = 0
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages = len(reader.pages)
            
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        return {
            "text": "",
            "title": f"ERROR: {e}",
            "sections": {"abstract": "", "introduction": "", "conclusion": ""},
            "metadata": {"pages": 0, "extraction_method": "failed", "sections_found": []}
        }

    # Extract title from filename
    title = Path(pdf_path).stem
    
    # Try to extract actual paper title (usually at the beginning)
    extracted_title = _extract_paper_title(text)
    if extracted_title:
        title = extracted_title
    
    # Extract sections
    sections, sections_found, method = _extract_sections_enhanced(text)
    
    return {
        "text": text,
        "title": title,
        "sections": sections,
        "metadata": {
            "pages": pages,
            "extraction_method": method,
            "sections_found": sections_found
        }
    }


def _extract_paper_title(text: str) -> Optional[str]:
    """
    Attempts to extract the paper title from the beginning of the text.
    Paper titles are usually in the first 500 characters and end before Abstract.
    """
    # Get first 1000 characters
    header = text[:1000]
    
    # Try to find text before "Abstract" keyword
    abstract_match = re.search(r'(.*?)\s*(?:Abstract|ABSTRACT)', header, re.IGNORECASE | re.DOTALL)
    if abstract_match:
        potential_title = abstract_match.group(1).strip()
        # Clean up: remove newlines, extra spaces
        potential_title = re.sub(r'\s+', ' ', potential_title)
        # Take first meaningful line (often the title)
        lines = potential_title.split('.')
        if lines and len(lines[0]) > 10:  # Title should be reasonably long
            return lines[0].strip()
    
    return None


def _normalize_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph breaks."""
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Preserve double newlines as paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _extract_sections_enhanced(text: str) -> tuple:
    """
    Enhanced section extraction with multiple patterns and fallback strategies.
    
    Returns: (sections_dict, sections_found_list, extraction_method)
    """
    text_normalized = _normalize_text(text)
    
    # Strategy 1: Try precise pattern matching
    sections, found = _extract_with_precise_patterns(text_normalized)
    if len(found) >= 2:  # At least 2 sections found
        return sections, found, "precise_patterns"
    
    # Strategy 2: Try relaxed pattern matching
    sections, found = _extract_with_relaxed_patterns(text_normalized)
    if len(found) >= 2:
        return sections, found, "relaxed_patterns"
    
    # Strategy 3: Try numbered sections (1. Introduction, etc.)
    sections, found = _extract_with_numbered_patterns(text_normalized)
    if len(found) >= 2:
        return sections, found, "numbered_patterns"
    
    # Strategy 4: Line-by-line header detection
    sections, found = _extract_with_line_detection(text)
    if len(found) >= 1:
        return sections, found, "line_detection"
    
    # Fallback: Return empty sections
    return {
        "abstract": "",
        "introduction": "",
        "conclusion": ""
    }, [], "failed"


def _extract_with_precise_patterns(text: str) -> tuple:
    """
    Extract using precise regex patterns that match section HEADINGS only.
    Handles: Roman numerals (I., II.), regular numbers (1., 2.), and standalone headings.
    Section can start a line with text continuing on same line (Abstract — text...)
    or be on separate line (Introduction\ntext).
    """
    sections = {"abstract": "", "introduction": "", "conclusion": ""}
    found = []
    
    # Abstract: At line start, optionally followed by dash/colon, text can be on same line
    abstract_patterns = [
        # Abstract at line start (with — or : separator), ends at Keywords/Introduction
        r"(?:^|\n)\s*(?:Abstract|ABSTRACT)\s*[—:\-–]\s*(.*?)\s*(?:Index Terms|Keywords|KEYWORDS|(?:I\.|1\.?|II\.)\s*(?:Introduction|INTRODUCTION))",
        # Abstract on its own line
        r"(?:^|\n)\s*(?:Abstract|ABSTRACT)\s*\n\s*(.*?)\s*(?:Index Terms|Keywords|Introduction)",
        # Abstract followed by blank line then section
        r"(?:^|\n)\s*(?:Abstract|ABSTRACT)\s*[—:\-–]?\s*(.*?)\s*(?:\n\s*\n\s*(?:I\.|1\.?|Introduction))"
    ]
    
    for pattern in abstract_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sections["abstract"] = match.group(1).strip()
            if len(sections["abstract"]) > 50:  # Sanity check
                found.append("abstract")
                break
    
    # Introduction: With Roman numerals (I., II.) or numbers (1., 2.) at line start
    intro_patterns = [
        # Roman numeral I. or number 1. at line start (may have no space: "I.INTRODUCTION")
        r"(?:^|\n)\s*(?:I\.|1\.?)\s*(?:Introduction|INTRODUCTION)\s*(.*?)\s*(?:(?:II\.|2\.?)\s*(?:[A-Z])|(?:\n\s*\n))",
        # Introduction at line start without numbering
        r"(?:^|\n)\s*(?:Introduction|INTRODUCTION)\s*\n\s*(.*?)\s*(?:(?:II\.|2\.)\s*[A-Z]|Background|Method)",
        # Introduction with various next sections
        r"(?:^|\n)\s*(?:I\.|1\.?)\s*(?:Introduction|INTRODUCTION)\s*(.*?)\s*(?:Related Work|Literature|Background|Methodology|II\.)"
    ]
    
    for pattern in intro_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sections["introduction"] = match.group(1).strip()
            if len(sections["introduction"]) > 100:  # Introduction should be substantial
                found.append("introduction")
                break
    
    # Conclusion: With Roman numerals (IV., V., VI., VII., VIII., etc.) or numbers at line start
    conclusion_patterns = [
        # Roman numerals (IV-X) or numbers (4-10) at line start (handles spaces: "C ONCLUSION")
        r"(?:^|\n)\s*(?:IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\.|4\.?|5\.?|6\.?|7\.?|8\.?|9\.?|10\.?)\s*(?:C\s*onclusion|Conclusion|CONCLUSION|C\s*ONCLUSION|Conclusions|CONCLUSIONS)\s*(.*?)\s*(?:References|REFERENCES|Acknowledgement|ACKNOWLEDGMENT|$)",
        # Conclusion without numbering
        r"(?:^|\n)\s*(?:Conclusion|CONCLUSION|C\s*ONCLUSION|Conclusions|CONCLUSIONS)\s*\n\s*(.*?)\s*(?:References|REFERENCES|Bibliography|$)",
        # Conclusion at line start with text on same line
        r"(?:^|\n)\s*(?:IV\.|V\.|VI\.|VII\.|7\.?|8\.?)\s*(?:C\s*onclusion|Conclusion|CONCLUSION)\s*[—:\-–]?\s*(.*?)\s*(?:References|$)"
    ]
    
    for pattern in conclusion_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sections["conclusion"] = match.group(1).strip()
            if len(sections["conclusion"]) > 50:
                found.append("conclusion")
                break
    
    return sections, found


def _extract_with_relaxed_patterns(text: str) -> tuple:
    """
    More flexible patterns that look for section headers at line starts.
    Handles Roman numerals, regular numbers, and text on same line as header.
    """
    sections = {"abstract": "", "introduction": "", "conclusion": ""}
    found = []
    
    # Try to split by section patterns at line starts
    # Handles: "Abstract —", "I.INTRODUCTION", "VII. Conclusion", etc.
    
    # Find Abstract
    abstract_match = re.search(
        r"(?:^|\n)\s*(?:Abstract|ABSTRACT)\s*[—:\-–]?\s*(.*?)\s*(?=\n\s*(?:Index Terms|Keywords|I\.|1\.|Introduction))",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if abstract_match:
        content = abstract_match.group(1).strip()
        if len(content) > 50:
            sections["abstract"] = content[:2000]
            found.append("abstract")
    
    # Find Introduction (handles I., II., 1., 2., or just "Introduction")
    intro_match = re.search(
        r"(?:^|\n)\s*(?:I\.|1\.?|)\s*(?:Introduction|INTRODUCTION)\s*(.*?)\s*(?=\n\s*(?:II\.|2\.|Related|Background|Method))",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if intro_match:
        content = intro_match.group(1).strip()
        if len(content) > 100:
            sections["introduction"] = content[:5000]
            found.append("introduction")
    
    # Find Conclusion (handles IV., V., VI., VII., VIII., etc. and spaces like "C ONCLUSION")
    conclusion_match = re.search(
        r"(?:^|\n)\s*(?:IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\.|4\.?|5\.?|6\.?|7\.?|8\.?|9\.?|10\.?|)\s*(?:C\s*onclusion|Conclusion|CONCLUSION|C\s*ONCLUSION|Conclusions|CONCLUSIONS)\s*[—:\-–]?\s*(.*?)\s*(?=\n\s*(?:References|REFERENCES|Acknowledgement|ACKNOWLEDGMENT|$))",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if conclusion_match:
        content = conclusion_match.group(1).strip()
        if len(content) > 50:
            sections["conclusion"] = content[:3000]
            found.append("conclusion")
    
    return sections, found


def _extract_with_numbered_patterns(text: str) -> tuple:
    """
    Extract sections that use numbered headers (1. Introduction, etc.).
    Ensures section names are headings, not inline text.
    """
    sections = {"abstract": "", "introduction": "", "conclusion": ""}
    found = []
    
    # Abstract might not be numbered, but should be on its own line
    abstract_match = re.search(
        r"(?:^|\n)\s*(?:Abstract|ABSTRACT)\s*[:\-]?\s*\n\s*(.*?)\s*(?:\n\s*1\s*\.|\n\s*\n)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if abstract_match:
        sections["abstract"] = abstract_match.group(1).strip()
        if len(sections["abstract"]) > 50:
            found.append("abstract")
    
    # Introduction usually numbered as 1. - must be at line start
    intro_match = re.search(
        r"(?:^|\n)\s*(?:1\s*\.?\s*Introduction|1\s*\.?\s*INTRODUCTION)\s*\n\s*(.*?)\s*(?:\n\s*2\s*\.)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if intro_match:
        sections["introduction"] = intro_match.group(1).strip()
        if len(sections["introduction"]) > 100:
            found.append("introduction")
    
    # Conclusion might be numbered section (4-10) - must be at line start (handles "C ONCLUSION" with space)
    conclusion_match = re.search(
        r"(?:^|\n)\s*(?:[4-9]\s*\.?\s*C\s*onclusion|[4-9]\s*\.?\s*Conclusion|[4-9]\s*\.?\s*CONCLUSION|[4-9]\s*\.?\s*C\s*ONCLUSION|[4-9]\s*\.?\s*Conclusions|[4-9]\s*\.?\s*CONCLUSIONS|10\s*\.?\s*C\s*onclusion|10\s*\.?\s*Conclusion)\s*\n\s*(.*?)\s*(?:\n\s*(?:References|REFERENCES|Acknowledgement|ACKNOWLEDGMENT)|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if conclusion_match:
        sections["conclusion"] = conclusion_match.group(1).strip()
        if len(sections["conclusion"]) > 50:
            found.append("conclusion")
    
    return sections, found


def _extract_with_line_detection(text: str) -> tuple:
    """
    Line-by-line detection for section headers.
    Only matches section names that are standalone on their own line.
    Handles optional numbering (e.g., "1. Introduction" or "Introduction").
    """
    sections = {"abstract": "", "introduction": "", "conclusion": ""}
    found = []
    
    lines = text.split('\n')
    current_section = None
    section_content = []
    
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Check if this line is a section header (with optional numbering)
        # Match patterns like: "Abstract", "1. Introduction", "5 Conclusion", etc.
        header_match = re.match(r'^(?:\d+\s*\.?\s*)?(abstract|introduction|conclusion|conclusions|references)$', line_lower)
        
        if header_match:
            section_name = header_match.group(1)
            
            # Save previous section
            if current_section and section_content:
                content = '\n'.join(section_content).strip()
                if current_section in sections and len(content) > 50:
                    sections[current_section] = content
                    found.append(current_section)
            
            # Start new section
            if section_name in ['abstract', 'introduction']:
                current_section = section_name
                section_content = []
            elif section_name in ['conclusion', 'conclusions']:
                current_section = 'conclusion'
                section_content = []
            elif section_name == 'references':
                # Stop processing at references
                break
            else:
                current_section = None
        else:
            # Add line to current section
            if current_section:
                section_content.append(line)
    
    # Save last section
    if current_section and section_content:
        content = '\n'.join(section_content).strip()
        if len(content) > 50:
            sections[current_section] = content
            if current_section not in found:
                found.append(current_section)
    
    return sections, found


def extract_key_sections(pdf_path: str) -> str:
    """
    Wrapper function for backward compatibility.
    Extracts key sections and returns them as formatted text.
    """
    result = extract_pdf_text(pdf_path)
    
    if not result or result["title"].startswith("ERROR"):
        return f"Failed to extract from {pdf_path}: {result.get('title', 'Unknown error')}"
    
    sections = result["sections"]
    metadata = result["metadata"]
    
    # Build formatted output
    output = []
    output.append(f"Title: {result['title']}")
    output.append(f"Pages: {metadata['pages']}")
    output.append(f"Extraction Method: {metadata['extraction_method']}")
    output.append(f"Sections Found: {', '.join(metadata['sections_found']) if metadata['sections_found'] else 'None'}")
    output.append("\n" + "="*80 + "\n")
    
    if sections["abstract"]:
        output.append("ABSTRACT:")
        output.append(sections["abstract"][:1000])  # Limit to 1000 chars
        output.append("\n" + "-"*80 + "\n")
    
    if sections["introduction"]:
        output.append("INTRODUCTION:")
        output.append(sections["introduction"][:2000])  # Limit to 2000 chars
        output.append("\n" + "-"*80 + "\n")
    
    if sections["conclusion"]:
        output.append("CONCLUSION:")
        output.append(sections["conclusion"][:1500])  # Limit to 1500 chars
        output.append("\n" + "-"*80 + "\n")
    
    return "\n".join(output)
