"""
Query routes for RAG system with answer generation.
Provides endpoints for semantic search and LLM-powered answer generation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rag.retriever import ClientVectorStore
from rag.generator import get_generator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    """Request model for document queries."""
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    """Response model for query results with generated answers."""
    query: str
    answer: str
    sources: list[str]
    retrieved_chunks: list[dict]
    generation_time_seconds: float
    context_chunks_used: int

@router.post("/{client_id}/query", response_model=QueryResponse)
async def query_documents(client_id: str, request: QueryRequest):
    """
    Query documents and generate an answer using retrieved context.

    This endpoint:
    1. Searches for relevant document chunks using semantic similarity
    2. Uses a local LLM to generate a natural language answer
    3. Returns the answer with source citations and retrieved chunks

    Args:
        client_id: Unique identifier for the client
        request: Query request with question and retrieval parameters

    Returns:
        QueryResponse with answer, sources, and metadata
    """
    try:
        # Validate input
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if request.top_k < 1 or request.top_k > 20:
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")

        logger.info(f"Processing query for client {client_id}: {request.query[:50]}...")

        # Initialize vector store for client
        store = ClientVectorStore(client_id)

        # Check if client has any documents
        doc_count = store.get_document_count()
        if doc_count == 0:
            return QueryResponse(
                query=request.query,
                answer="No documents found for this client. Please ingest some documents first.",
                sources=[],
                retrieved_chunks=[],
                generation_time_seconds=0.0,
                context_chunks_used=0
            )

        # Retrieve relevant chunks
        retrieved_chunks = store.search(request.query, request.top_k)

        if not retrieved_chunks:
            return QueryResponse(
                query=request.query,
                answer="No relevant information found in the documents.",
                sources=[],
                retrieved_chunks=[],
                generation_time_seconds=0.0,
                context_chunks_used=0
            )

        # Generate answer using local LLM
        generator = get_generator()
        generation_result = generator.generate_answer(
            query=request.query,
            context_chunks=retrieved_chunks
        )

        # Format response
        response = QueryResponse(
            query=request.query,
            answer=generation_result["answer"],
            sources=generation_result["sources"],
            retrieved_chunks=retrieved_chunks,
            generation_time_seconds=generation_result["generation_time_seconds"],
            context_chunks_used=generation_result["context_chunks_used"]
        )

        logger.info(f"Query completed for client {client_id} in {generation_result['generation_time_seconds']:.2f}s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query for client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{client_id}/documents")
async def list_client_documents(client_id: str):
    """
    List all documents available for a client.

    Args:
        client_id: Unique identifier for the client

    Returns:
        List of document names
    """
    try:
        store = ClientVectorStore(client_id)
        documents = store.list_documents()

        return {
            "client_id": client_id,
            "documents": documents,
            "total_documents": len(documents)
        }

    except Exception as e:
        logger.error(f"Error listing documents for client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{client_id}/documents")
async def clear_client_documents(client_id: str):
    """
    Clear all documents for a client (for testing/reset purposes).

    Args:
        client_id: Unique identifier for the client

    Returns:
        Confirmation message
    """
    try:
        store = ClientVectorStore(client_id)
        initial_count = store.get_document_count()

        store.delete_all()

        return {
            "message": f"Cleared {initial_count} documents for client {client_id}",
            "client_id": client_id
        }

    except Exception as e:
        logger.error(f"Error clearing documents for client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
