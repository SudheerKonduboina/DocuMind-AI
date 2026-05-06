# System Architecture

## Overview

The AI Document Q&A application follows a clean modular architecture with nginx as the production entry point, providing reverse proxy capabilities, request buffering, and security.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
│                     (React + Vite Frontend)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS/HTTP
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Nginx Reverse Proxy                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Request Buffering (Disk for large, RAM for small)      │  │
│  │  • Gzip Compression                                        │  │
│  │  • Rate Limiting                                            │  │
│  │  • SSL Termination (future)                                 │  │
│  │  • Static File Serving                                      │  │
│  │  • Keepalive Connections                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Server                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Modular Architecture                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │  │
│  │  │   Auth   │  │ Document │  │ Chatbot  │  │  Media  │ │  │
│  │  │  Module  │  │  Module  │  │  Module  │  │ Module  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │   Summ   │  │ Playback │  │ Vector   │              │  │
│  │  │  Module  │  │  Module  │  │  Search  │              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │              Core Infrastructure                  │  │  │
│  │  │  • Config  • Database  • Security  • Logging      │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ↓                    ↓                    ↓
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  PostgreSQL     │  │     Redis       │  │  FAISS Vector   │
│  + pgvector     │  │   (Cache)       │  │     Store       │
│                 │  │                 │  │                 │
│  • Users        │  │  • Session      │  │  • Embeddings   │
│  • Documents    │  │  • Query Cache  │  │  • Index        │
│  • Chats        │  │  • Rate Limit   │  │                 │
│  • Transcripts  │  │                 │  │                 │
│  • Summaries    │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ↓
                    ┌─────────────────┐
                    │  External APIs  │
                    │                 │
                    │  • OpenAI       │
                    │  • AWS S3       │
                    │  • Whisper      │
                    └─────────────────┘
```

## Nginx Request Buffering Strategy

Nginx implements intelligent request buffering to optimize performance:

### Large Requests (File Uploads > 128KB)
- **Buffering**: Disk-based buffering
- **Configuration**: `client_body_buffer_size 128k`, `proxy_request_buffering on`
- **Behavior**: Request bodies larger than 128KB are buffered to disk in `/var/tmp/nginx`
- **Benefits**: 
  - Prevents memory exhaustion during large file uploads
  - Allows backend to process uploads at its own pace
  - Enables upload resume capability
  - Protects against slow-upload attacks

### Small Requests (API Calls < 128KB)
- **Buffering**: Memory-based buffering
- **Configuration**: Default memory buffers (4k-8k)
- **Behavior**: Request bodies smaller than 128KB are kept in RAM
- **Benefits**:
  - Faster processing (no disk I/O)
  - Lower latency for typical API calls
  - Reduced CPU overhead

### Streaming Responses (Chat Endpoints)
- **Buffering**: Disabled
- **Configuration**: `proxy_buffering off` for `/chats/` endpoint
- **Behavior**: Responses are streamed directly to client without buffering
- **Benefits**:
  - Real-time streaming for AI responses
  - Lower time-to-first-byte
  - Better user experience for chat interactions

## Module Structure

Each module follows clean architecture principles:

```
modules/
├── auth/
│   ├── auth_controller.py    # HTTP request handling
│   ├── auth_router.py         # Route definitions
│   ├── auth_service.py        # Business logic
│   ├── auth_repository.py     # Data access
│   ├── auth_models.py         # SQLAlchemy models
│   ├── auth_schemas.py        # Pydantic schemas
│   └── __init__.py            # Public API exports
```

### Public API Pattern

Each module exposes only clean public interfaces via `__init__.py`:

```python
from .auth_router import router as auth_router
from .auth_service import AuthService

__all__ = ["auth_router", "AuthService"]
```

This hides internal implementation details and provides a clean module boundary.

## Data Flow

1. **Client Request** → Nginx (port 80)
2. **Nginx** → Rate limiting, buffering, compression
3. **Nginx** → FastAPI Backend (port 8000)
4. **FastAPI** → Module Router → Controller → Service → Repository
5. **Repository** → PostgreSQL / Redis / FAISS
6. **Service** → External APIs (OpenAI, AWS S3)
7. **Response** → Nginx → Client

## Security Layers

1. **Nginx Layer**: Rate limiting, request size limits, security headers
2. **FastAPI Layer**: JWT authentication, CORS, input validation
3. **Service Layer**: Business logic validation, authorization checks
4. **Database Layer**: Row-level security, encrypted connections

## Scalability Considerations

- **Horizontal Scaling**: Backend can be scaled behind nginx load balancer
- **Database**: PostgreSQL with pgvector for vector similarity search
- **Caching**: Redis for session management and query caching
- **Vector Search**: FAISS index persisted in dedicated volume
- **File Storage**: AWS S3 for document storage and retrieval

## Deployment Architecture

```
Production Environment:
┌─────────────────────────────────────────┐
│         Cloud Provider (AWS/GCP)        │
│  ┌───────────────────────────────────┐  │
│  │  Load Balancer / CDN              │  │
│  └───────────────┬───────────────────┘  │
│                  │                      │
│  ┌───────────────▼───────────────────┐  │
│  │  Nginx Reverse Proxy (Multiple)  │  │
│  └───────────────┬───────────────────┘  │
│                  │                      │
│  ┌───────────────▼───────────────────┐  │
│  │  FastAPI Backend (Auto-scaled)   │  │
│  └───────────────┬───────────────────┘  │
│                  │                      │
│  ┌───────────────▼───────────────────┐  │
│  │  Managed PostgreSQL + pgvector  │  │
│  │  Managed Redis                  │  │
│  │  Persistent FAISS Storage       │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
```
