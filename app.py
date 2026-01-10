from fastapi import FastAPI
from fastapi.responses import FileResponse
from routes.ingest import router as ingest_router
from routes.query import router as query_router
from routes.clients import router as clients_router

app = FastAPI(
    title="Enterprise RAG System",
    description="Client-isolated Retrieval-Augmented Generation API",
    version="1.0.0"
)

app.include_router(ingest_router, prefix="/clients", tags=["Ingestion"])
app.include_router(query_router, prefix="/clients", tags=["Query"])
app.include_router(clients_router, tags=["Clients"])

@app.get("/")
async def root():
    """Serve the main frontend page."""
    return FileResponse("index.html", media_type="text/html")

@app.get("/health")
def health_check():
    return {"status": "ok"}