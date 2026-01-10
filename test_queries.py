#!/usr/bin/env python3
"""
Test script for the RAG system query functionality.
Demonstrates retrieval and answer generation capabilities.
"""

import requests
import json
import time
from typing import List, Dict, Any

API_BASE_URL = "http://127.0.0.1:8000"
CLIENT_ID = "client_001"

def test_query(query: str, top_k: int = 3, description: str = "") -> Dict[str, Any]:
    """Test a single query and return the results."""
    print(f"\n{'='*60}")
    if description:
        print(f"🧪 {description}")
    print(f"❓ Query: {query}")
    print(f"🎯 Top-K: {top_k}")
    print(f"{'='*60}")

    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/clients/{CLIENT_ID}/query",
            json={"query": query, "top_k": top_k},
            timeout=60  # Allow more time for LLM generation
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            total_time = end_time - start_time

            print("✅ Query successful!")
            print(f"⏱️  Total time: {total_time:.2f}s")
            print(f"🤖 Generated Answer:")
            print(f"   {result['answer']}")
            print(f"\n📚 Sources: {', '.join(result['sources'])}")
            print(f"📄 Chunks used: {result['context_chunks_used']}")
            print(f"⏱️  Generation time: {result['generation_time_seconds']:.2f}s")

            if result['retrieved_chunks']:
                print(f"\n🔍 Retrieved Chunks Preview:")
                for i, chunk in enumerate(result['retrieved_chunks'][:2], 1):  # Show first 2 chunks
                    metadata = chunk['metadata']
                    print(f"   Chunk {i}: {metadata['document_name']} - {metadata['section']}")
                    print(f"   \"{chunk['text'][:150]}...\"")
                    print(f"   Score: {chunk.get('score', 'N/A'):.3f}")

            return result
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Query error: {e}")
        return None

def test_health_check():
    """Test the health endpoint."""
    print("\n🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_list_documents():
    """Test listing client documents."""
    print("\n📋 Testing document listing...")
    try:
        response = requests.get(f"{API_BASE_URL}/clients/{CLIENT_ID}/documents")
        if response.status_code == 200:
            result = response.json()
            print("✅ Document listing successful!")
            print(f"📁 Client: {result['client_id']}")
            print(f"📄 Documents: {', '.join(result['documents'])}")
            print(f"📊 Total: {result['total_documents']}")
            return result
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Document listing error: {e}")
        return None

def main():
    """Run comprehensive query tests."""
    print("🚀 Starting RAG System Query Tests")
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"👤 Client ID: {CLIENT_ID}")

    # Test health check
    if not test_health_check():
        print("❌ System health check failed. Aborting tests.")
        return

    # Test document listing
    docs_result = test_list_documents()
    if not docs_result or docs_result['total_documents'] == 0:
        print("❌ No documents found. Please run ingest_bulk_docs.py first.")
        return

    # Comprehensive query tests
    test_queries = [
        {
            "query": "What are the employee benefits offered by the company?",
            "description": "Benefits Query",
            "top_k": 3
        },
        {
            "query": "How does the performance management system work?",
            "description": "HR Performance Query",
            "top_k": 3
        },
        {
            "query": "What security measures should employees follow?",
            "description": "Security Guidelines Query",
            "top_k": 4
        },
        {
            "query": "What is the remote work policy?",
            "description": "Remote Work Query",
            "top_k": 3
        },
        {
            "query": "What happens during employee termination?",
            "description": "Termination Process Query",
            "top_k": 3
        },
        {
            "query": "How much vacation time do employees get?",
            "description": "Vacation Policy Query",
            "top_k": 2
        },
        {
            "query": "What training and development opportunities are available?",
            "description": "Professional Development Query",
            "top_k": 3
        },
        {
            "query": "What is the company's code of conduct?",
            "description": "Ethics & Conduct Query",
            "top_k": 4
        }
    ]

    results = []
    for test_case in test_queries:
        result = test_query(**test_case)
        if result:
            results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful queries: {len(results)}/{len(test_queries)}")
    print(f"❌ Failed queries: {len(test_queries) - len(results)}")

    if results:
        avg_generation_time = sum(r['generation_time_seconds'] for r in results) / len(results)
        total_chunks_used = sum(r['context_chunks_used'] for r in results)
        unique_sources = set()
        for r in results:
            unique_sources.update(r['sources'])

        print(f"⏱️  Average generation time: {avg_generation_time:.2f}s")
        print(f"📄 Total context chunks used: {total_chunks_used}")
        print(f"📚 Unique sources cited: {len(unique_sources)}")
        print(f"🔍 Sources: {', '.join(sorted(unique_sources))}")

    print(f"\n🎉 RAG System testing complete!")
    print("💡 The system successfully combines retrieval and generation for enterprise document Q&A!")

if __name__ == "__main__":
    main()
