# 🤖 Enterprise RAG System

An AI-powered document assistant that provides intelligent answers to questions about enterprise policies, HR guidelines, security protocols, and company procedures using local Large Language Models (no external API costs).

![Demo](https://via.placeholder.com/800x400/667eea/ffffff?text=Enterprise+RAG+Demo)

## 🌟 Features

- **📄 Multi-format Support**: Processes PDF and DOCX documents
- **🔍 Semantic Search**: Uses HuggingFace embeddings for accurate retrieval
- **🤖 Local AI**: GPT4All integration (no paid API dependencies)
- **🏢 Client Isolation**: Separate knowledge bases per client
- **🎨 Modern UI**: Interactive web interface with sample questions
- **🚀 Easy Deployment**: Docker, Railway, Render support
- **📊 Vector Storage**: ChromaDB for efficient similarity search

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/enterprise-rag.git
cd enterprise-rag

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --reload

# Open your browser
# Frontend: http://127.0.0.1:8000
# API Docs: http://127.0.0.1:8000/docs
```

### Docker Deployment

```bash
# Build the image
docker build -t enterprise-rag .

# Run the container
docker run -p 8000:8000 enterprise-rag
```

##  Usage

### 1. Document Ingestion

Upload your enterprise documents (PDF/DOCX) to the `data/` folder, then run:

```bash
python3 ingest_bulk_docs.py
```

This will:
- Extract text from all documents
- Split into 200-word chunks with metadata
- Store in ChromaDB vector database

### 2. Ask Questions

**Via Web Interface:**
- Visit `http://127.0.0.1:8000`
- Click sample questions or ask your own
- Get AI-generated answers with source citations

**Via API:**
```bash
curl -X POST "http://127.0.0.1:8000/clients/client_001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the vacation policy?", "top_k": 3}'
```

##  Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Documents     │───▶│   Chunking      │───▶│   Vector        │
│   (PDF/DOCX)    │    │   (200 words)    │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌─────────────────┐               │
│   User Query    │───▶│   Retrieval     │◀──────────────┘
└─────────────────┘    │   (Top-K)       │
                       └─────────────────┘
                                 │
                       ┌─────────────────┐
                       │   Generation    │
                       │   (GPT4All)     │
                       └─────────────────┘
                                 │
                       ┌─────────────────┐
                       │   AI Answer     │
                       │   + Sources     │
                       └─────────────────┘
```

##  Project Structure

```
enterprise-rag/
├── app.py                 # FastAPI application
├── index.html            # Frontend interface
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── render.yaml         # Render deployment
├── railway.json        # Railway deployment
├── ingest_bulk_docs.py # Bulk document ingestion
├── test_queries.py     # Query testing script
├── data/               # Document storage
├── vectorstores/       # Vector database storage
├── routes/             # API route handlers
│   ├── ingest.py       # Document ingestion endpoints
│   ├── query.py        # Query endpoints
│   └── clients.py      # Client management
└── rag/                # RAG components
    ├── chunker.py      # Document chunking
    ├── retriever.py    # Vector search
    └── generator.py    # LLM generation
```

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - Web interface
- `GET /health` - Health check
- `GET /docs` - API documentation

### Client Management
- `GET /clients` - List all clients

### Document Operations
- `POST /clients/{client_id}/ingest` - Ingest documents
- `GET /clients/{client_id}/documents` - List client documents
- `DELETE /clients/{client_id}/documents` - Clear client documents

### Query Operations
- `POST /clients/{client_id}/query` - Ask questions and get AI answers

## 🚀 Deployment Options

### Railway (Recommended)
1. Fork this repository
2. Connect to Railway
3. Deploy automatically
4. Access your live app!

### Render
1. Fork this repository
2. Connect to Render
3. Use the `render.yaml` configuration
4. Deploy with one click

### Docker
```bash
docker build -t enterprise-rag .
docker run -p 8000:8000 enterprise-rag
```

### Other Platforms
The app works on any platform that supports Python 3.12:
- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Google Cloud Run

##  Sample Documents

The system comes with comprehensive sample documents:
- **HR Policy** (PDF) - Employment policies and procedures
- **IT Security Guidelines** (DOCX) - Security protocols and compliance
- **Employee Benefits** (PDF) - Benefits and compensation details
- **Remote Work Policy** (PDF) - Work-from-home guidelines
- **Code of Conduct** (PDF) - Ethical standards and behavior
- **Holiday Policy** (PDF) - Time-off and leave policies

##  Testing

Run comprehensive tests:

```bash
# Test document ingestion
python3 ingest_bulk_docs.py

# Test queries
python3 test_queries.py
```

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

##  License

MIT License - feel free to use this project for your own purposes!

##  Acknowledgments

- **FastAPI** - Modern Python web framework
- **ChromaDB** - Vector database for AI applications
- **GPT4All** - Local LLM inference
- **HuggingFace** - Transformer models and embeddings
- **Sentence Transformers** - Text embeddings

---

