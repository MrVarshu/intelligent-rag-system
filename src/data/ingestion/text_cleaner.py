import re

def clean_text(text: str) -> str:
    # removing multiple blank lines, weird unicode, and long whitespace
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def simple_chunk(text: str, max_chars: int = 2000):
    """
    Splits text into chunks of up to max_chars using sentence boundaries,
    avoids breaking words or sentences across chunks.
    """
    if not text:
        return []

    # Normalize line breaks
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Regex to split sentences: ends with ., !, ? followed by space or line break
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    cur_chunk = []
    cur_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        s_len = len(sentence)
        # If adding this sentence exceeds max_chars, flush current chunk
        if cur_len + s_len > max_chars and cur_chunk:
            chunks.append(" ".join(cur_chunk))
            cur_chunk = [sentence]
            cur_len = s_len
        else:
            cur_chunk.append(sentence)
            cur_len += s_len + 1  # +1 for space

    # Add last chunk
    if cur_chunk:
        chunks.append(" ".join(cur_chunk))

    return chunks