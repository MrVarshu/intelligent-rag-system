"""
This module implements a complete RAG (Retrieval-Augmented Generation) pipeline
using LangChain's ChatGroq with PromptTemplate for cleaner, more reusable code.
"""

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from src.data.vectorstore.chroma_client import query as chroma_query
from src.config.settings import GROQ_API_KEY, GROQ_MODEL

# For token limit exceeded errors 
MAX_CONTEXT_CHARS = 30000  # Roughly ~7500 tokens (4 chars per token estimate)

# Creates and returns a ChatGroq instance
def get_chatgroq_llm(model: str = None, temperature: float = 0.7, max_tokens: int = 1000):
    model = GROQ_MODEL 
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return llm

def generate_response(query: str, context: str, model: str = None, temperature: float = 0.7, max_tokens: int = 1000):
    """
    Generate a response using ChatGroq with PromptTemplate (LCEL).
    
    Args:
        query: The user's question
        context: The retrieved context from ChromaDB
        model: Groq model to use (defaults to GROQ_MODEL from settings)
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum tokens in the response
        
    Returns:
        The generated response string
    """
    # Create ChatGroq instance
    llm = get_chatgroq_llm(model=model, temperature=temperature, max_tokens=max_tokens)
    
    # Create prompt template
    prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Your role is to answer questions STRICTLY based on the provided context. "
               "If the answer is not in the context, say 'I don't have enough information in the provided context to answer that question.' "
               "Do NOT use your training knowledge. ONLY use the information given in the context below."),
    ("human", """Context:{context}
    Question: {question}
    # Please provide a detailed but concise answer based ONLY on the context above. "
    # Include key points and explanations clearly without being too lengthy.""")
    ])
    
    try:
        chain = prompt_template | llm
        response = chain.invoke({"context": context, "question": query})
        return response.content
    
    except Exception as e:
        return f"Error generating response: {str(e)}"


def main():
    """
    Example usage of the ChatGroq-based query system with PromptTemplate.
    """
    # Example queries
    example_queries = [
        "What is artificial intelligence?",
        "Explain data mining techniques?",
    ]
    
    for query in example_queries:
        print("\n" + "="*80)
        
        result = answer_query(query, n_results=2)
        
        print(f"\nQuery: {result['query']}")
        print(f"Method: {result['method']}")
        print(f"\nAnswer:\n{result['answer']}")
        print("\n" + "="*80)



def retrieve_context(query_text: str, n_results: int = 5, max_chars: int = MAX_CONTEXT_CHARS):
    """
    Retrieve relevant documents from ChromaDB for the given query.
    Also returns metadata for display (source, section, similarity).
    """
    results = chroma_query(query_text, n_results=n_results)

    if not results or not results.get('documents') or not results['documents'][0]:
        return "No relevant context found in the database.", []

    documents = results['documents'][0]
    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]

    context_parts = []
    retrieved_docs = []
    total_chars = 0
    docs_included = 0

    for idx, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
        source = metadata.get('source', 'Unknown')
        section = metadata.get('section', 'Unknown')
        chunk_index = metadata.get('chunk_index', idx)

        # Convert distance → similarity (assuming cosine distance)
        try:
            similarity = max(0.0, min(1.0, 1.0 - float(distance)))
        except Exception:
            similarity = None

        # Short preview for display
        snippet = doc[:300] + ("..." if len(doc) > 300 else "")

        # Truncate for context safety
        if len(doc) > 5000:
            doc = doc[:5000] + "... [truncated]"

        doc_text = f"[Document {idx+1}] (Source: {source}, Section: {section})\n{doc}"

        # Stop if exceeding max_chars
        if total_chars + len(doc_text) > max_chars:
            if docs_included == 0:
                remaining = max_chars - total_chars - 200
                context_parts.append(doc_text[:remaining] + "... [truncated]")
                docs_included += 1
            break

        context_parts.append(doc_text)
        total_chars += len(doc_text)
        docs_included += 1

        # Store document stats for display
        retrieved_docs.append({
            "doc_index": idx + 1,
            "source": source,
            "section": section,
            "chunk_index": chunk_index,
            "distance": distance,
            "similarity": similarity,
            "snippet": snippet,
        })

    context = "\n\n".join(context_parts)

    if docs_included < len(documents):
        context += f"\n\n[Note: Showing {docs_included} of {len(documents)} retrieved documents due to size limits]"

    return context, retrieved_docs



def answer_query(query: str, n_results: int = 3, model: str = None, temperature: float = 0.7, max_tokens: int = 1000):
    # Retrieve context + metadata
    context, retrieved_docs = retrieve_context(query, n_results=n_results)

    # Generate response using existing pipeline (no prompt change)
    answer = generate_response(query, context, model=model, temperature=temperature, max_tokens=max_tokens)

    return {
        "query": query,
        "answer": answer,
        "method": "ChatGroq with PromptTemplate (LCEL)",
        "retrieved_docs": retrieved_docs,
        "context": context
    }


if __name__ == "__main__":
    main()
