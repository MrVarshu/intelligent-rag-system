"""
Interactive Query Interface
Run this script to interactively query your ChromaDB using Groq LLM.
"""

from src.query_system import answer_query


def main():
    print("="*80)
    print("RAG Query System - Interactive Mode")
    print("="*80)
    print("\nThis system will:")
    print("1. Convert your query to embeddings")
    print("2. Search for relevant documents in ChromaDB")
    print("3. Generate a response using Groq LLM based ONLY on retrieved context")
    print("\nType 'quit' or 'exit' to stop.\n")
    
    while True:
        print("-"*80)
        query = input("\nEnter your query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not query:
            print("Please enter a valid query.")
            continue
        
        try:
            # Get number of results (optional)
            n_input = input("Number of documents to retrieve (default: 3, max recommended: 5): ").strip()
            n_results = int(n_input) if n_input else 3
            
            # Warn if too many documents requested
            if n_results > 5:
                print(f"⚠️  Warning: Requesting {n_results} documents may exceed token limits.")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    n_results = 3
                    print(f"Using default: {n_results} documents")
            
            # Process the query
            result = answer_query(query, n_results=n_results)
            
            # Display results
            print("\n" + "="*80)
            print(f"QUERY: {result['query']}")
            print("="*80)
            print(f"\nANSWER:\n{result['answer']}")
            print("\n" + "="*80)
            
            # Optionally show context
            show_context = input("\nShow retrieved context? (y/n): ").strip().lower()
            if show_context == 'y':
                print("\nRETRIEVED CONTEXT:")
                print("-"*80)
                print(result['context'])
                print("-"*80)
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")


if __name__ == "__main__":
    main()
