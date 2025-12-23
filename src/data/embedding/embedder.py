from sentence_transformers import SentenceTransformer
from typing import List
from src.config.settings import EMBEDDING_MODEL

_model = None

# Loading the embedding model
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

# Embedding texts
def embed_texts(texts: List[str]):
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings.tolist()