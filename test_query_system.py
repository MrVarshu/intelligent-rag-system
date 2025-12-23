"""
Test script to verify the query system is working correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    try:
        from src.query_system import answer_query, retrieve_context, generate_response
        print("✓ Query system imports successful")
        
        from src.data.vectorstore.chroma_client import query, collection
        print("✓ ChromaDB client imports successful")
        
        from src.data.embedding.embedder import embed_texts
        print("✓ Embedder imports successful")
        
        from src.config.settings import GROQ_API_KEY, GROQ_MODEL
        print("✓ Settings imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        return False


def test_chromadb():
    """Test ChromaDB connection and collection."""
    print("\nTesting ChromaDB...")
    try:
        from src.data.vectorstore.chroma_client import collection
        count = collection.count()
        print(f"✓ ChromaDB connection successful")
        print(f"  Collection 'papers' contains {count} documents")
        return count > 0
    except Exception as e:
        print(f"✗ ChromaDB test failed: {str(e)}")
        return False


def test_embeddings():
    """Test embedding generation."""
    print("\nTesting embeddings...")
    try:
        from src.data.embedding.embedder import embed_texts
        test_text = ["This is a test sentence"]
        embeddings = embed_texts(test_text)
        print(f"✓ Embedding generation successful")
        print(f"  Embedding dimension: {len(embeddings[0])}")
        return True
    except Exception as e:
        print(f"✗ Embedding test failed: {str(e)}")
        return False


def test_groq_api():
    """Test Groq API connection."""
    print("\nTesting Groq API...")
    try:
        from groq import Groq
        from src.config.settings import GROQ_API_KEY, GROQ_MODEL
        
        if not GROQ_API_KEY:
            print("✗ GROQ_API_KEY not set in .env file")
            return False
        
        client = Groq(api_key=GROQ_API_KEY)
        
        # Simple test call using the model from settings
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'test successful' in 2 words"}],
            model=GROQ_MODEL,  # Use the model from settings
            max_tokens=10
        )
        
        print(f"✓ Groq API connection successful")
        print(f"  Model: {GROQ_MODEL}")
        print(f"  Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"✗ Groq API test failed: {str(e)}")
        return False


def test_query_system():
    """Test the complete query system."""
    print("\nTesting complete query system...")
    try:
        from src.query_system import answer_query
        
        # Use a simple query
        result = answer_query("What information is available?", n_results=2)
        
        print(f"✓ Query system test successful")
        print(f"  Query: {result['query']}")
        print(f"  Answer length: {len(result['answer'])} characters")
        print(f"  Context retrieved: {len(result['context'])} characters")
        
        return True
    except Exception as e:
        print(f"✗ Query system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*80)
    print("RAG Query System - Test Suite")
    print("="*80)
    
    tests = [
        ("Imports", test_imports),
        ("ChromaDB", test_chromadb),
        ("Embeddings", test_embeddings),
        ("Groq API", test_groq_api),
        ("Query System", test_query_system),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    print("\n" + "="*80)
    if all_passed:
        print("All tests passed! ✓")
        print("You can now use the query system:")
        print("  python interactive_query.py")
    else:
        print("Some tests failed. Please check the errors above.")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
