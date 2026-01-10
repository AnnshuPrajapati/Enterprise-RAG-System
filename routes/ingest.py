from fastapi import APIRouter
from pydantic import BaseModel
from rag.retriever import ClientVectorStore

router = APIRouter()

class IngestRequest(BaseModel):
    document_name: str
    text: str
    metadata: dict

@router.post("/{client_id}/ingest")
def ingest_documents(client_id: str, request: IngestRequest):
    store = ClientVectorStore(client_id)

    store.add_texts(
        texts=[request.text],
        metadatas=[{
            "document": request.document_name,
            **request.metadata
        }]
    )

    return {
        "status": "success",
        "client_id": client_id
    }
