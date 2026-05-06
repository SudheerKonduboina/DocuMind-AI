# Sequence Diagrams

## Upload Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth
    participant S3
    participant Processor
    participant Whisper
    participant Embedder
    participant FAISS
    participant PG
    participant Redis
    participant Summarizer
    
    User->>Frontend: Drag & drop file
    Frontend->>Frontend: Validate file
    Frontend->>API: POST /documents/upload (multipart)
    API->>Auth: Validate JWT
    Auth-->>API: User ID
    API->>S3: Upload file
    S3-->>API: S3 key
    API->>PG: Create document record
    PG-->>API: Document ID
    API-->>Frontend: Document ID (status: processing)
    
    par Async Processing
        API->>Processor: Start processing
        Processor->>Processor: Determine file type
        
        alt PDF
            Processor->>Processor: Extract text
            Processor->>Processor: Chunk document
        else Audio/Video
            Processor->>Whisper: Transcribe
            Whisper-->>Processor: Transcript + timestamps
            Processor->>Processor: Chunk transcript
        end
        
        Processor->>Embedder: Generate embeddings
        Embedder-->>Processor: Vectors
        Processor->>FAISS: Index vectors
        Processor->>PG: Store chunks + embeddings
        Processor->>PG: Update document status
        Processor->>Redis: Cache document info
        Processor->>Summarizer: Trigger summary
    end
    
    Frontend->>API: Poll document status
    API-->>Frontend: Status: completed
    Frontend->>User: Show success
```

## Chat Query Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth
    participant Redis
    participant FAISS
    participant PG
    participant OpenAI
    participant Playback
    
    User->>Frontend: Type question
    Frontend->>API: POST /chats/{id}/messages
    API->>Auth: Validate JWT
    Auth-->>API: User ID
    API->>Redis: Check rate limit
    Redis-->>API: Allowed
    API->>Redis: Check cache
    alt Cache Hit
        Redis-->>API: Cached response
        API-->>Frontend: Stream cached response
    else Cache Miss
        API->>API: Generate query embedding
        API->>FAISS: Search similar vectors
        FAISS-->>API: Top-k chunk IDs
        API->>PG: Retrieve chunks
        PG-->>API: Chunk content + metadata
        API->>API: Build context prompt
        API->>OpenAI: Send prompt (streaming)
        loop Stream tokens
            OpenAI-->>API: Token chunk
            API->>Playback: Extract timestamp
            Playback-->>API: Timestamp (if found)
            API-->>Frontend: SSE: token + timestamp
        end
        API->>Redis: Cache response
    end
    Frontend->>Frontend: Display streaming text
    Frontend->>User: Show clickable timestamps
```

## Timestamp Playback Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth
    participant PG
    participant S3
    participant Player
    
    User->>Frontend: Click timestamp badge
    Frontend->>API: GET /playback/{doc_id}/segment?timestamp=12.5
    API->>Auth: Validate JWT
    Auth-->>API: User ID
    API->>PG: Get transcript segments
    PG-->>API: Segment data
    API->>API: Calculate start/end (±30s)
    API->>S3: Get media URL
    S3-->>API: Presigned URL
    API-->>Frontend: {start_time, end_time, transcript, s3_url}
    Frontend->>Player: Load media
    Frontend->>Player: Seek to start_time
    Player->>User: Play segment
```

## Summarization Pipeline Sequence Diagram

```mermaid
sequenceDiagram
    participant Upload
    participant Queue
    participant Summarizer
    participant PG
    participant OpenAI
    participant Redis
    
    Upload->>Queue: Enqueue summary task
    Queue->>Summarizer: Pick up task
    Summarizer->>PG: Get document chunks
    PG-->>Summarizer: Chunks
    Summarizer->>Summarizer: Build summary prompt
    Summarizer->>OpenAI: Request summary
    OpenAI-->>Summarizer: Summary text
    Summarizer->>PG: Store summary
    PG-->>Summarizer: Summary ID
    Summarizer->>Redis: Cache summary
    Summarizer->>Queue: Mark complete
    
    Note over User,Redis: On-demand summary
    User->>API: GET /summaries/{doc_id}
    API->>Redis: Check cache
    alt Cache Hit
        Redis-->>API: Cached summary
    else Cache Miss
        API->>PG: Get summary
        PG-->>API: Summary
        API->>Redis: Cache summary
    end
    API-->>User: Summary
```

## Authentication Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Auth
    participant PG
    participant Redis
    
    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>Auth: Validate credentials
    Auth->>PG: Query user
    PG-->>Auth: User record
    Auth->>Auth: Verify password hash
    Auth->>Auth: Generate JWT
    Auth->>Redis: Store session
    Auth-->>API: JWT token
    API-->>Frontend: {access_token, user}
    Frontend->>Frontend: Store token
    
    Note over User,Redis: Subsequent requests
    User->>Frontend: Access protected resource
    Frontend->>API: Request with Authorization header
    API->>Auth: Validate JWT
    Auth->>Redis: Check session
    Redis-->>Auth: Valid
    Auth-->>API: User ID
    API-->>Frontend: Resource data
```

## Rate Limiting Sequence Diagram

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant RateLimiter
    
    Client->>API: Request
    API->>RateLimiter: Check limit
    RateLimiter->>Redis: Get current count
    Redis-->>RateLimiter: Count
    RateLimiter->>RateLimiter: Check threshold
    alt Under limit
        RateLimiter->>Redis: Increment count
        RateLimiter->>Redis: Set expiry
        RateLimiter-->>API: Allowed
        API->>API: Process request
        API-->>Client: Response
    else Over limit
        RateLimiter-->>API: Denied
        API-->>Client: 429 Too Many Requests
    end
```

## Vector Search Sequence Diagram

```mermaid
sequenceDiagram
    participant Query
    participant Embedder
    participant FAISS
    participant PG
    participant Ranker
    
    Query->>Embedder: Query text
    Embedder->>Embedder: Generate embedding
    Embedder-->>Query: Query vector
    
    Query->>FAISS: Search(query_vector, k=10)
    FAISS-->>Query: Top-k chunk IDs + scores
    
    Query->>PG: Retrieve chunks by IDs
    PG-->>Query: Chunk metadata
    
    Query->>Ranker: Re-rank by relevance
    Ranker-->>Query: Ranked chunks
    
    Query->>Query: Filter by user_id
    Query-->>Query: Final results
```
