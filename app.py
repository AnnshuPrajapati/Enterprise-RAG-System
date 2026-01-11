from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.ingest import router as ingest_router
from routes.query import router as query_router
from routes.clients import router as clients_router
import os

app = FastAPI(
    title="Enterprise RAG System",
    description="Client-isolated Retrieval-Augmented Generation API",
    version="1.0.0"
)

# Add CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/clients", tags=["Ingestion"])
app.include_router(query_router, prefix="/clients", tags=["Query"])
app.include_router(clients_router, tags=["Clients"])

@app.get("/")
async def root():
    """Serve the main frontend page."""
    return FileResponse("index.html", media_type="text/html")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Enterprise RAG System is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}