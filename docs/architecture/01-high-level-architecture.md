# High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        FE[Frontend - React/Vite/TypeScript]
    end
    
    subgraph "API Gateway Layer"
        NGINX[Nginx Reverse Proxy]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend]
        AUTH[Auth Module]
        DOC[Document Module]
        MEDIA[Media Module]
        CHAT[Chatbot Module]
        SUMM[Summarization Module]
        VS[Vector Search Module]
        PLAY[Playback Module]
    end
    
    subgraph "AI/ML Layer"
        OPENAI[OpenAI API]
        WHISPER[Whisper ASR]
        LANGCHAIN[LangChain]
        LLAMAINDEX[LlamaIndex]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL + pgvector)]
        REDIS[(Redis)]
        FAISS[FAISS Vector Store]
        S3[AWS S3]
    end
    
    subgraph "Infrastructure"
        EC2[AWS EC2]
        DOCKER[Docker Compose]
        GHA[GitHub Actions]
    end
    
    FE --> NGINX
    NGINX --> API
    
    API --> AUTH
    API --> DOC
    API --> MEDIA
    API --> CHAT
    API --> SUMM
    API --> VS
    API --> PLAY
    
    CHAT --> OPENAI
    CHAT --> LANGCHAIN
    CHAT --> LLAMAINDEX
    MEDIA --> WHISPER
    
    VS --> FAISS
    VS --> PG
    
    AUTH --> REDIS
    API --> REDIS
    DOC --> S3
    MEDIA --> S3
    
    PG --> PG
    REDIS --> REDIS
    FAISS --> FAISS
    S3 --> S3
    
    DOCKER --> API
    DOCKER --> FE
    DOCKER --> PG
    DOCKER --> REDIS
    DOCKER --> FAISS
    DOCKER --> NGINX
    
    GHA --> DOCKER
    DOCKER --> EC2
```

## Architecture Overview

### Client Layer
- **Frontend**: React + Vite + TypeScript
- Modern SaaS UI with streaming chat, drag-drop uploads, media player

### API Gateway Layer
- **Nginx**: Reverse proxy, SSL termination, load balancing

### Application Layer
- **FastAPI**: High-performance async Python framework
- Modular architecture with feature-based separation
- JWT authentication, rate limiting, caching

### AI/ML Layer
- **OpenAI API**: GPT models for chat and summarization
- **Whisper**: Audio/video transcription
- **LangChain + LlamaIndex**: RAG pipeline orchestration

### Data Layer
- **PostgreSQL + pgvector**: Relational data + vector similarity
- **Redis**: Caching, rate limiting, session management
- **FAISS**: High-performance vector search
- **AWS S3**: File storage (documents, media)

### Infrastructure
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD pipeline
- **AWS EC2**: Production deployment
