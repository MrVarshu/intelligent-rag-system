"""
Simple RAG Query System
This module takes a user query, converts it to embeddings, retrieves relevant context 
from ChromaDB, and generates a response using Groq LLM.
"""

import os
from groq import Groq
from src.data.vectorstore.chroma_client import query as chroma_query
from src.config.settings import GROQ_API_KEY, GROQ_MODEL

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Token limits for context (leaving room for system prompt, query, and response)
MAX_CONTEXT_CHARS = 30000  # Roughly ~7500 tokens (4 chars per token estimate)


def retrieve_context(query_text: str, n_results: int = 5, max_chars: int = MAX_CONTEXT_CHARS):
    """
    Retrieve relevant documents from ChromaDB based on the query.
    
    Args:
        query_text: The user's query
        n_results: Number of similar documents to retrieve
        max_chars: Maximum characters to include in context (to avoid token limits)
        
    Returns:
        A formatted context string with retrieved documents
    """
    results = chroma_query(query_text, n_results=n_results)
    
    if not results or not results.get('documents') or not results['documents'][0]:
        return "No relevant context found in the database."
    
    # Format the retrieved documents into context
    context_parts = []
    documents = results['documents'][0]
    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]
    
    total_chars = 0
    docs_included = 0
    
    for idx, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
        source = metadata.get('source', 'Unknown')
        
        # Truncate individual document if it's too long
        if len(doc) > 5000:
            doc = doc[:5000] + "... [truncated]"
        
        doc_text = f"[Document {idx+1}] (Source: {source})\n{doc}"
        
        # Check if adding this document would exceed the limit
        if total_chars + len(doc_text) > max_chars:
            if docs_included == 0:
                # Include at least one document, even if truncated
                remaining = max_chars - total_chars - 200  # Leave some buffer
                doc_text = doc_text[:remaining] + "... [truncated]"
                context_parts.append(doc_text)
                docs_included += 1
            break
        
        context_parts.append(doc_text)
        total_chars += len(doc_text)
        docs_included += 1
    
    context = "\n\n".join(context_parts)
    
    if docs_included < len(documents):
        context += f"\n\n[Note: Showing {docs_included} of {len(documents)} retrieved documents due to size limits]"
    
    return context


def generate_response(query: str, context: str, model: str = None, temperature: float = 0.7, max_tokens: int = 1000):
    """
    Generate a response using Groq LLM based on the retrieved context.
    
    Args:
        query: The user's question
        context: The retrieved context from ChromaDB
        model: Groq model to use (defaults to GROQ_MODEL from settings)
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum tokens in the response
        
    Returns:
        The generated response string
    """
    model = model or GROQ_MODEL or "llama-3.3-70b-versatile"
    
    # Create a system prompt that restricts the model to only use provided context
    system_prompt = (
        "You are a helpful AI assistant. Your role is to answer questions STRICTLY based on the provided context. "
        "If the answer is not in the context, say 'I don't have enough information in the provided context to answer that question.' "
        "Do NOT use your training knowledge. ONLY use the information given in the context below."
    )
    # Create the user prompt with context and question
    user_prompt = f"""Context:
    {context}
    Question: {query}
    Please provide a clear and concise answer based ONLY on the context above."""
    
    try:
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        return f"Error generating response: {str(e)}"


def answer_query(query: str, n_results: int = 3, model: str = None, temperature: float = 0.7, max_tokens: int = 1000):
    """
    Complete RAG pipeline: retrieve context and generate answer.
    
    Args:
        query: The user's question
        n_results: Number of documents to retrieve from ChromaDB (default: 3, reduced to avoid token limits)
        model: Groq model to use
        temperature: Controls randomness in generation
        max_tokens: Maximum tokens in response
        
    Returns:
        A dictionary containing the answer, context, and metadata
    """
    print(f"Processing query: {query}")
    print(f"Retrieving {n_results} relevant documents from ChromaDB...")
    
    # Step 1: Retrieve context from ChromaDB (with automatic truncation)
    context = retrieve_context(query, n_results=n_results)
    
    # Show context size info
    context_chars = len(context)
    estimated_tokens = context_chars // 4  # Rough estimate: 4 chars per token
    print(f"Context size: {context_chars} chars (~{estimated_tokens} tokens)")
    
    print("Generating response using Groq LLM...")
    
    # Step 2: Generate response using Groq
    answer = generate_response(query, context, model=model, temperature=temperature, max_tokens=max_tokens)
    
    return {
        "query": query,
        "answer": answer,
        "context": context,
        "n_results": n_results
    }


def main():
    """
    Example usage of the query system.
    """
    # Example queries
    example_queries = [
        "What is artificial intelligence?",
        "Summarize the main topics in the documents",
    ]
    
    for query in example_queries:
        print("\n" + "="*80)
        result = answer_query(query, n_results=3)
        
        print(f"\nQuery: {result['query']}")
        print(f"\nAnswer:\n{result['answer']}")
        print("\n" + "="*80)


if __name__ == "__main__":
    main()
