# Component Diagram

```mermaid
graph TB
    subgraph "Frontend Components"
        AUTH_UI[Auth Components]
        UPLOAD_UI[Upload Components]
        CHAT_UI[Chat Components]
        MEDIA_UI[Media Components]
        SUMMARY_UI[Summary Components]
        PLAYER_UI[Player Components]
    end
    
    subgraph "Backend Modules"
        AUTH_MOD[Auth Module]
        DOC_MOD[Document Module]
        MEDIA_MOD[Media Module]
        CHAT_MOD[Chatbot Module]
        SUMM_MOD[Summarization Module]
        VS_MOD[Vector Search Module]
        PLAY_MOD[Playback Module]
    end
    
    subgraph "Core Services"
        CONFIG[Config Service]
        DB[Database Service]
        CACHE[Cache Service]
        S3_CLIENT[S3 Client]
        OPENAI_CLIENT[OpenAI Client]
    end
    
    subgraph "Data Stores"
        PG_DB[(PostgreSQL)]
        REDIS_DB[(Redis)]
        FAISS_DB[FAISS Index]
        S3_BUCKET[(S3 Bucket)]
    end
    
    AUTH_UI --> AUTH_MOD
    UPLOAD_UI --> DOC_MOD
    UPLOAD_UI --> MEDIA_MOD
    CHAT_UI --> CHAT_MOD
    MEDIA_UI --> MEDIA_MOD
    MEDIA_UI --> PLAY_MOD
    SUMMARY_UI --> SUMM_MOD
    PLAYER_UI --> PLAY_MOD
    
    AUTH_MOD --> CONFIG
    AUTH_MOD --> DB
    AUTH_MOD --> CACHE
    
    DOC_MOD --> CONFIG
    DOC_MOD --> DB
    DOC_MOD --> S3_CLIENT
    DOC_MOD --> VS_MOD
    
    MEDIA_MOD --> CONFIG
    MEDIA_MOD --> DB
    MEDIA_MOD --> S3_CLIENT
    MEDIA_MOD --> OPENAI_CLIENT
    MEDIA_MOD --> VS_MOD
    
    CHAT_MOD --> CONFIG
    CHAT_MOD --> DB
    CHAT_MOD --> CACHE
    CHAT_MOD --> OPENAI_CLIENT
    CHAT_MOD --> VS_MOD
    CHAT_MOD --> PLAY_MOD
    
    SUMM_MOD --> CONFIG
    SUMM_MOD --> DB
    SUMM_MOD --> CACHE
    SUMM_MOD --> OPENAI_CLIENT
    SUMM_MOD --> VS_MOD
    
    VS_MOD --> CONFIG
    VS_MOD --> DB
    VS_MOD --> FAISS_DB
    
    PLAY_MOD --> CONFIG
    PLAY_MOD --> DB
    
    DB --> PG_DB
    CACHE --> REDIS_DB
    S3_CLIENT --> S3_BUCKET
```

## Component Details

### Frontend Components

#### Auth Components
- `LoginPage`: User login form
- `RegisterPage`: User registration form
- `AuthGuard`: Route protection wrapper
- `AuthProvider`: Authentication context

#### Upload Components
- `UploadCenter`: Drag-drop upload interface
- `FileUploader`: Individual file upload handler
- `UploadProgress`: Progress indicator
- `FileList`: Uploaded files display

#### Chat Components
- `ChatInterface`: Main chat UI
- `MessageList`: Message history display
- `MessageItem`: Single message component
- `ChatInput`: Input field with send button
- `TimestampBadge`: Clickable timestamp indicator
- `StreamingResponse`: Real-time token display

#### Media Components
- `MediaLibrary`: File browser
- `MediaCard`: File preview card
- `MediaFilter`: Filter controls
- `MediaSearch`: Search functionality

#### Summary Components
- `SummaryViewer`: Summary display
- `SummaryCard`: Individual summary
- `SummaryActions`: Edit/regenerate options

#### Player Components
- `MediaPlayer`: Video/audio player
- `TimestampControls`: Jump to segment
- `PlaybackControls`: Play/pause/seek

### Backend Modules

#### Auth Module
- `controller.py`: Request handlers
- `service.py`: Business logic
- `repository.py`: Data access
- `schemas.py`: Pydantic models
- `models.py`: SQLAlchemy models
- `router.py`: FastAPI routes

#### Document Module
- PDF text extraction
- Document chunking
- Metadata storage
- S3 upload handling

#### Media Module
- Audio/video upload
- Whisper transcription
- Timestamp extraction
- S3 storage

#### Chatbot Module
- RAG pipeline
- Context injection
- Streaming responses
- Query processing

#### Summarization Module
- Auto-summary generation
- On-demand summarization
- Summary storage

#### Vector Search Module
- FAISS index management
- Embedding generation
- Semantic search
- pgvector operations

#### Playback Module
- Timestamp mapping
- Segment extraction
- Playback API

### Core Services

#### Config Service
- Environment variable loading
- Configuration validation
- Settings management

#### Database Service
- Connection pooling
- Session management
- Migration handling

#### Cache Service
- Redis connection
- Cache operations
- Rate limiting

#### S3 Client
- File upload/download
- Bucket management
- URL generation

#### OpenAI Client
- API authentication
- Request handling
- Response parsing
