# import hashlib


# def make_id(source: str, text: str) -> str:
#     # deterministic id for a chunk (source could be URL or file path)
#     h = hashlib.sha1((source + text[:200]).encode('utf-8')).hexdigest()
#     return f"{h}"


# src/data/vectorstore/vector_utils.py
import hashlib
import base64
import re

def make_id(source_id: str, chunk_index: int) -> str:
    """
    Create deterministic, short id for a source+chunk_index.
    """
    base = f"{source_id}::{chunk_index}"
    base = re.sub(r"\s+", "_", base)
    h = hashlib.sha1(base.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(h).decode("utf-8").rstrip("=")
