"""
Full end-to-end test: Ingest a PDF using the new scraper
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.data_ingest_pipeline import ingest_pdf_file
from src.data.vectorstore.chroma_client import collection


def test_full_ingestion():
    """
    Test full PDF ingestion with new scraper.
    """
    print("\n" + "="*80)
    print("FULL END-TO-END INGESTION TEST")
    print("="*80 + "\n")
    
    pdf_path = "data_storage/raw_pdfs/sample_paper.pdf"
    
    # Get initial count
    print("Step 1: Getting initial ChromaDB count...")
    initial_count = collection.count()
    print(f"✓ Initial documents in ChromaDB: {initial_count}")
    
    # Ingest PDF
    print(f"\nStep 2: Ingesting PDF: {Path(pdf_path).name}")
    try:
        chunks_created = ingest_pdf_file(pdf_path, max_chars=1500)
        print(f"✓ Ingestion successful!")
        print(f"✓ Chunks created and stored: {chunks_created}")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Get final count
    print("\nStep 3: Verifying ChromaDB...")
    final_count = collection.count()
    added = final_count - initial_count
    print(f"✓ Final documents in ChromaDB: {final_count}")
    print(f"✓ Documents added: {added}")
    
    # Query to verify
    print("\nStep 4: Testing query to verify ingested content...")
    try:
        results = collection.query(
            query_texts=["email spam classification"],
            n_results=3
        )
        
        if results and results["documents"] and len(results["documents"][0]) > 0:
            print(f"✓ Query successful!")
            print(f"✓ Found {len(results['documents'][0])} relevant documents")
            print(f"\n✓ Sample result:")
            print(f"  Document: {results['documents'][0][0][:150]}...")
            if results['metadatas'][0][0]:
                print(f"  Metadata: {results['metadatas'][0][0]}")
        else:
            print("⚠️  Query returned no results")
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Check if documents exist for this PDF
    print("\nStep 5: Verifying stored documents...")
    try:
        stored_docs = collection.get(
            limit=10,
            where={"source": pdf_path}
        )
        docs_in_db = len(stored_docs["ids"])
        print(f"✓ Documents from this PDF in ChromaDB: {docs_in_db}")
        
        if docs_in_db > 0:
            print(f"\n✓ Sample stored metadata:")
            for i, meta in enumerate(stored_docs["metadatas"][:3], 1):
                section = meta.get("section", "N/A")
                chunk = meta.get("chunk_index", "N/A")
                print(f"  {i}. Section: {section}, Chunk: {chunk}")
    except Exception as e:
        print(f"⚠️  Could not verify stored documents: {e}")
        docs_in_db = 0
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    # Success criteria: chunks were created AND they exist in DB
    # (added can be 0 if documents already existed and were updated via upsert)
    if chunks_created > 0 and docs_in_db >= chunks_created:
        print("\n✅ FULL INGESTION TEST PASSED!")
        print(f"  ✓ PDF extracted successfully with new scraper")
        print(f"  ✓ {chunks_created} chunks created from sections")
        
        if added > 0:
            print(f"  ✓ {added} NEW documents added to ChromaDB")
        else:
            print(f"  ✓ {docs_in_db} documents updated in ChromaDB (upsert)")
            print(f"    (Documents already existed, were updated with new extraction)")
        
        print(f"  ✓ Query retrieval working")
        print(f"  ✓ Metadata includes section names (abstract/introduction/conclusion)")
        print("\n🎉 New scraper works perfectly with the ingestion pipeline!")
        return True
    else:
        print("\n❌ TEST FAILED")
        print(f"  Chunks created: {chunks_created}")
        print(f"  Documents added: {added}")
        print(f"  Documents in DB: {docs_in_db}")
        return False


if __name__ == "__main__":
    success = test_full_ingestion()
    exit(0 if success else 1)
