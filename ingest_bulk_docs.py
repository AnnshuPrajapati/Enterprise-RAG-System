#!/usr/bin/env python3
"""
Bulk document ingestion script for Enterprise RAG system.
Reads PDFs and DOCX files from data/ directory, extracts text,
chunks into 200-word pieces using advanced chunking, and ingests to the API.
"""

import os
import requests
import glob
from PyPDF2 import PdfReader
from docx import Document
import json
from typing import List, Dict, Any
from rag.chunker import chunk_document

API_BASE_URL = "http://127.0.0.1:8000"
CLIENT_ID = "client_001"

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ Error reading PDF {filepath}: {e}")
        return ""

def extract_text_from_docx(filepath: str) -> str:
    """Extract text from a DOCX file."""
    try:
        doc = Document(filepath)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Skip empty paragraphs
                text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ Error reading DOCX {filepath}: {e}")
        return ""

def get_document_name(filepath: str) -> str:
    """Extract document name from filepath."""
    return os.path.splitext(os.path.basename(filepath))[0]

def get_source_filename(filepath: str) -> str:
    """Get the full source filename with extension."""
    return os.path.basename(filepath)

def ingest_chunk(client_id: str, chunk_data: Dict[str, Any]) -> bool:
    """Ingest a single chunk to the API."""
    url = f"{API_BASE_URL}/clients/{client_id}/ingest"

    payload = {
        "document_name": chunk_data["metadata"]["document_name"],
        "text": chunk_data["text"],
        "metadata": chunk_data["metadata"]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            metadata = chunk_data["metadata"]
            doc_name = metadata["document_name"]
            chunk_id = metadata["chunk_id"]
            total_chunks = metadata["total_chunks"]
            print(f"✅ Ingested {doc_name} chunk {chunk_id}/{total_chunks}")
            return True
        else:
            metadata = chunk_data["metadata"]
            doc_name = metadata["document_name"]
            chunk_id = metadata["chunk_id"]
            print(f"❌ Failed to ingest {doc_name} chunk {chunk_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        metadata = chunk_data["metadata"]
        doc_name = metadata["document_name"]
        chunk_id = metadata["chunk_id"]
        print(f"❌ Error ingesting {doc_name} chunk {chunk_id}: {e}")
        return False

def process_document(filepath: str) -> int:
    """Process a single document: extract text, chunk it, and ingest chunks."""
    document_name = get_document_name(filepath)
    source_file = get_source_filename(filepath)

    # Extract text based on file type
    if filepath.endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
    elif filepath.endswith('.docx'):
        text = extract_text_from_docx(filepath)
    else:
        print(f"❌ Unsupported file type: {filepath}")
        return 0

    if not text:
        print(f"❌ No text extracted from {filepath}")
        return 0

    # Use advanced chunking with metadata
    chunks = chunk_document(text, document_name, source_file, chunk_size=200)

    print(f"📄 Processing {document_name}: {len(text)} chars → {len(chunks)} chunks")

    # Ingest each chunk
    success_count = 0
    for chunk_data in chunks:
        if ingest_chunk(CLIENT_ID, chunk_data):
            success_count += 1

    return success_count

def main():
    """Main ingestion process."""
    print("🚀 Starting bulk document ingestion...")
    print(f"📁 Client ID: {CLIENT_ID}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print("📚 Using advanced chunking with metadata preservation")

    # Find all PDF and DOCX files in data directory
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found!")
        return

    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    docx_files = glob.glob(os.path.join(data_dir, "*.docx"))
    all_files = pdf_files + docx_files

    if not all_files:
        print(f"❌ No PDF or DOCX files found in {data_dir}/")
        return

    print(f"📋 Found {len(all_files)} documents: {len(pdf_files)} PDFs, {len(docx_files)} DOCX")

    # Process each document
    total_chunks = 0
    successful_chunks = 0

    for filepath in sorted(all_files):
        chunks_ingested = process_document(filepath)
        total_chunks += chunks_ingested
        successful_chunks += chunks_ingested

    print(f"\n🎉 Ingestion complete!")
    print(f"📊 Total chunks processed: {successful_chunks}")

    # Test the ingestion by checking if we can query
    print(f"\n🔍 Testing ingestion with a sample query...")
    test_query()

def test_query():
    """Test the ingestion by making a sample query."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/clients/{CLIENT_ID}/query",
            json={"query": "What are the employee benefits?", "top_k": 3},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Query test successful!")
            print(f"🤖 Answer: {result['answer'][:100]}...")
            print(f"📚 Sources: {', '.join(result['sources'])}")
            print(".2f")
        else:
            print(f"❌ Query test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Query test error: {e}")

if __name__ == "__main__":
    main()