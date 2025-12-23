import chromadb
from src.data.embedding.embedder import embed_texts
# Create client
from chromadb import Client
try:
    client = chromadb.PersistentClient("./data_storage/chroma_db")
except Exception as e:
    print(f"[WARN] PersistentClient failed, falling back to ephemeral Client(): {e}")
    client = chromadb.Client()

COLLECTION_NAME = "papers"

try:
    collection = client.get_collection(COLLECTION_NAME)
except Exception:
    collection = client.create_collection(name=COLLECTION_NAME)

# Insert or update documents
def add_documents(doc_texts, metadatas, ids, embeddings=None, upsert=True):
    """
    Insert or update documents into the collection.
    By default uses upsert to replace existing ids (safe for re-ingestion).
    If upsert=False, will call collection.add (which will error on duplicate ids).
    """
    if embeddings is None:
        embeddings = embed_texts(doc_texts)
    if upsert:
        if embeddings is not None:
            collection.upsert(documents=doc_texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        else:
            collection.upsert(documents=doc_texts, metadatas=metadatas, ids=ids)
    else:
        if embeddings is not None:
            collection.add(documents=doc_texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        else:
            collection.add(documents=doc_texts, metadatas=metadatas, ids=ids)

def query(query_text: str, n_results: int = 5, where: dict = None):
    """
    Perform similarity search by embedding the query text and querying with embeddings.
    Returns documents, metadatas, and distances from ChromaDB.
    """
    query_embedding = embed_texts([query_text])[0]  # embed_texts returns List[List[float]]
    
    res = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"]
    )
    return res
