# import PyPDF2
# import re

# def extract_pdf_text(pdf_path):
#     """
#     Extracts all text from a PDF file.
#     """
#     text = ""
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         for page in reader.pages:
#             text += page.extract_text() + "\n"
#     return text

# def extract_sections(text):
#     """
#     Extracts Abstract, Introduction, and Conclusion from text.
#     """
#     # Normalize whitespace
#     text = re.sub(r'\s+', ' ', text)

#     # Patterns for sections: only match exact capitalization as header
#     abstract_pattern = r"(?:Abstract|ABSTRACT)\s*[:\-]?\s*(.*?)\s*(?:Introduction|INTRODUCTION)"
#     introduction_pattern = r"(?:Introduction|INTRODUCTION)\s*[:\-]?\s*(.*?)\s*(?:Methods|METHODOLOGY|Materials|RESULTS|Conclusion|CONCLUSION)"
#     conclusion_pattern = r"(?:Conclusion|CONCLUSION)\s*[:\-]?\s*(.*?)(?:References|REFERENCES|ACKNOWLEDGEMENT|ACKNOWLEDGEMENTS|$)"

#     # No re.IGNORECASE so it only matches correct capitalization
#     abstract = re.search(abstract_pattern, text, re.DOTALL)
#     introduction = re.search(introduction_pattern, text, re.DOTALL)
#     conclusion = re.search(conclusion_pattern, text, re.DOTALL)

#     return {
#         "abstract": abstract.group(1).strip() if abstract else "Not Found",
#         "introduction": introduction.group(1).strip() if introduction else "Not Found",
#         "conclusion": conclusion.group(1).strip() if conclusion else "Not Found"
#     }

# if __name__ == "__main__":
#     pdf_path = "data_storage/raw_pdfs/sample_paper.pdf"  # Replace with your PDF path
#     full_text = extract_pdf_text(pdf_path)
#     sections = extract_sections(full_text)

#     print("=== Abstract ===")
#     print(sections['abstract'])
#     print("\n=== Introduction ===")
#     print(sections['introduction'])
#     print("\n=== Conclusion ===")
#     print(sections['conclusion'])

# import PyPDF2
# import re

# def extract_pdf_text(pdf_path):
#     """
#     Extracts all text from a PDF file.
#     """
#     text = ""
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         for page in reader.pages:
#             text += page.extract_text() + "\n"
#     return text

# def extract_sections(text):
#     """
#     Extracts Abstract, Introduction, and Conclusion from text.
#     """
#     # Normalize whitespace
#     text = re.sub(r'\s+', ' ', text)

#     # Patterns for sections
#     abstract_pattern = r"(?:Abstract|ABSTRACT)\s*[:\-]?\s*(.*?)\s*(?:Introduction|INTRODUCTION)"
#     introduction_pattern = r"(?:Introduction|INTRODUCTION)\s*[:\-]?\s*(.*?)\s*(?:Methods|METHODOLOGY|Materials|RESULTS|Conclusion|CONCLUSION)"
#     conclusion_pattern = r"(?:Conclusion|CONCLUSION)\s*[:\-]?\s*(.*?)(?:References|ACKNOWLEDGEMENTS|$)"

#     abstract = re.search(abstract_pattern, text, re.IGNORECASE | re.DOTALL)
#     introduction = re.search(introduction_pattern, text, re.IGNORECASE | re.DOTALL)
#     conclusion = re.search(conclusion_pattern, text, re.IGNORECASE | re.DOTALL)

#     return {
#         "abstract": abstract.group(1).strip() if abstract else "Not Found",
#         "introduction": introduction.group(1).strip() if introduction else "Not Found",
#         "conclusion": conclusion.group(1).strip() if conclusion else "Not Found"
#     }

# if __name__ == "__main__":
#     pdf_path = "data_storage/raw_pdfs/sample_paper.pdf"  # Replace with your PDF path
#     full_text = extract_pdf_text(pdf_path)
#     sections = extract_sections(full_text)

#     print("=== Abstract ===")
#     print(sections['abstract'])
#     print("\n=== Introduction ===")
#     print(sections['introduction'])
#     print("\n=== Conclusion ===")
#     print(sections['conclusion'])



# src/data/ingestion/pdf_scraper.py

# import PyPDF2
# import re
# from pathlib import Path

# def extract_pdf_text(pdf_path: str):
#     """
#     Extracts all text from a PDF file and returns a dict:
#       { "text": "...", "title": "<filename or PDF title if found>" }
#     """
#     text = ""
#     try:
#         with open(pdf_path, 'rb') as file:
#             reader = PyPDF2.PdfReader(file)
#             for page in reader.pages:
#                 page_text = page.extract_text() or ""
#                 text += page_text + "\n"
#     except Exception as e:
#         # Return empty text + include error in title for visibility
#         return {"text": "", "title": f"ERROR: {e}"}

#     # Title fallback to filename
#     title = Path(pdf_path).stem
#     return {"text": text, "title": title}


# def extract_sections(text: str):
#     """
#     Extracts Abstract, Introduction, and Conclusion from text.
#     Returns dict with keys 'abstract', 'introduction', 'conclusion'.
#     """
#     text_norm = re.sub(r'\s+', ' ', text)

#     abstract_pattern = r"(?:Abstract|ABSTRACT)\s*[:\-]?\s*(.*?)\s*(?:Introduction|INTRODUCTION)"
#     introduction_pattern = r"(?:Introduction|INTRODUCTION)\s*[:\-]?\s*(.*?)\s*(?:Methods|METHODOLOGY|Materials|RESULTS|Conclusion|CONCLUSION)"
#     conclusion_pattern = r"(?:Conclusion|CONCLUSION)\s*[:\-]?\s*(.*?)(?:References|ACKNOWLEDGEMENTS|$)"

#     abstract = re.search(abstract_pattern, text_norm, re.IGNORECASE | re.DOTALL)
#     introduction = re.search(introduction_pattern, text_norm, re.IGNORECASE | re.DOTALL)
#     conclusion = re.search(conclusion_pattern, text_norm, re.IGNORECASE | re.DOTALL)

#     return {
#         "abstract": abstract.group(1).strip() if abstract else "Not Found",
#         "introduction": introduction.group(1).strip() if introduction else "Not Found",
#         "conclusion": conclusion.group(1).strip() if conclusion else "Not Found"
#     }



# src/data/ingestion/pdf_scraper.py
import PyPDF2
import re
from pathlib import Path
from typing import Dict

def _normalize_whitespace(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()

def extract_pdf_text(pdf_path: str) -> Dict[str, any]:
    """
    Extracts full text and returns only Abstract, Introduction, Conclusion.
    Returns dict:
      {
        "text": "<full_text>",
        "title": "<filename>",
        "sections": {
            "abstract": "...",
            "introduction": "...",
            "conclusion": "..."
        }
      }
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        return {"text": "", "title": f"ERROR: {e}", "sections": {"abstract": "", "introduction": "", "conclusion": ""}}

    text_norm = _normalize_whitespace(text)
    title = Path(pdf_path).stem

    # regex patterns
    abstract_pattern = r"(?:Abstract|ABSTRACT)\s*[:\-]?\s*(.*?)\s*(?:Introduction|INTRODUCTION)"
    introduction_pattern = r"(?:Introduction|INTRODUCTION)\s*[:\-]?\s*(.*?)\s*(?:Conclusion|CONCLUSION|$)"
    conclusion_pattern = r"(?:Conclusion|CONCLUSION)\s*[:\-]?\s*(.*?)(?:References|$)"

    abstract = re.search(abstract_pattern, text_norm, re.IGNORECASE | re.DOTALL)
    introduction = re.search(introduction_pattern, text_norm, re.IGNORECASE | re.DOTALL)
    conclusion = re.search(conclusion_pattern, text_norm, re.IGNORECASE | re.DOTALL)

    sections = {
        "abstract": abstract.group(1).strip() if abstract else "",
        "introduction": introduction.group(1).strip() if introduction else "",
        "conclusion": conclusion.group(1).strip() if conclusion else ""
    }

    return {
        "text": text_norm,
        "title": title,
        "sections": sections
    }
