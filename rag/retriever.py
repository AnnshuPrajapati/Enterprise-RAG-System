"""
Vector store implementation using ChromaDB with HuggingFace embeddings.
Provides client-isolated document storage and retrieval.
"""

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import hashlib

class ClientVectorStore:
    """
    Client-isolated vector store using ChromaDB.
    Each client gets their own ChromaDB collection for complete data isolation.
    """

    def __init__(self, client_id: str, persist_directory: str = "vectorstores"):
        """
        Initialize client-specific vector store.

        Args:
            client_id: Unique identifier for the client
            persist_directory: Directory to persist ChromaDB data
        """
        self.client_id = client_id
        self.persist_directory = persist_directory

        # Create client-specific directory
        self.client_dir = os.path.join(persist_directory, client_id)
        os.makedirs(self.client_dir, exist_ok=True)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=self.client_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize sentence transformer for embeddings
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Get or create collection for this client
        collection_name = f"client_{client_id}_docs"
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
        except (ValueError, Exception):
            # Collection doesn't exist, create it
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"client_id": client_id}
            )

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Add text chunks with metadata to the vector store.

        Args:
            texts: List of text chunks to embed and store
            metadatas: List of metadata dictionaries for each text chunk
        """
        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must have the same length")

        if not texts:
            return

        # Generate embeddings
        embeddings = self.embedder.encode(texts).tolist()

        # Generate unique IDs for each chunk
        ids = []
        for i, metadata in enumerate(metadatas):
            # Create unique ID based on document name, chunk_id, and content hash
            content_hash = hashlib.md5(texts[i].encode()).hexdigest()[:8]
            chunk_id = metadata.get('chunk_id', i)
            doc_name = metadata.get('document_name', 'unknown')
            unique_id = f"{doc_name}_{chunk_id}_{content_hash}"
            ids.append(unique_id)

        # Convert metadata to ChromaDB format (string values only)
        chroma_metadatas = []
        for metadata in metadatas:
            chroma_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    chroma_metadata[key] = value
                else:
                    chroma_metadata[key] = str(value)
            chroma_metadatas.append(chroma_metadata)

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=chroma_metadatas,
            ids=ids
        )

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic similarity.

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing matched documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.encode([query]).tolist()[0]

        # Search the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['metadatas']:
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                result = {
                    'text': doc,
                    'metadata': metadata,
                    'score': 1.0 - results['distances'][0][i] if results['distances'] else 0.0
                }
                formatted_results.append(result)

        return formatted_results

    def get_document_count(self) -> int:
        """Get the total number of documents/chunks in the store."""
        return self.collection.count()

    def delete_all(self) -> None:
        """Delete all documents from the collection (for testing/reset)."""
        # Get all IDs and delete them
        results = self.collection.get(include=[])
        if results['ids']:
            self.collection.delete(ids=results['ids'])

    def list_documents(self) -> List[str]:
        """List all unique document names in the collection."""
        results = self.collection.get(include=['metadatas'])
        doc_names = set()
        for metadata in results['metadatas']:
            if 'document_name' in metadata:
                doc_names.add(metadata['document_name'])
        return sorted(list(doc_names))
