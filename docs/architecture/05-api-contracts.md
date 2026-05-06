# API Contract Documentation

## Base URL
```
Production: https://api.ai-doc-qa.com
Development: http://localhost:8000
```

## Authentication
All endpoints (except auth) require JWT Bearer token:
```
Authorization: Bearer <jwt_token>
```

---

## Auth Endpoints

### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

### POST /auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### GET /auth/me
Get current user info.

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Document Endpoints

### POST /documents/upload
Upload a document (PDF, audio, or video).

**Request:** `multipart/form-data`
- `file`: File (max 500MB)
- `title`: String (optional)

**Response (201):**
```json
{
  "id": "uuid",
  "title": "Document Title",
  "file_type": "pdf",
  "file_size": 1234567,
  "status": "processing",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /documents
List user's documents.

**Query Params:**
- `page`: Integer (default: 1)
- `limit`: Integer (default: 20)
- `file_type`: String (optional filter)

**Response (200):**
```json
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "items": [
    {
      "id": "uuid",
      "title": "Document Title",
      "file_type": "pdf",
      "file_size": 1234567,
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### GET /documents/{document_id}
Get document details.

**Response (200):**
```json
{
  "id": "uuid",
  "title": "Document Title",
  "file_type": "pdf",
  "file_size": 1234567,
  "status": "completed",
  "s3_key": "path/to/file",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### DELETE /documents/{document_id}
Delete a document.

**Response (204):** No content

---

## Chat Endpoints

### POST /chats
Create a new chat session.

**Request Body:**
```json
{
  "document_id": "uuid",
  "title": "Chat about Document"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "document_id": "uuid",
  "title": "Chat about Document",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /chats
List user's chats.

**Query Params:**
- `document_id`: UUID (optional filter)

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Chat about Document",
      "document_id": "uuid",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /chats/{chat_id}/messages
Send a message and get streaming response.

**Request Body:**
```json
{
  "content": "What is the main topic?"
}
```

**Response (200):** `text/event-stream`
```
data: {"token": "The", "timestamp": null}
data: {"token": " main", "timestamp": null}
data: {"token": " topic", "timestamp": "12.5"}
data: {"token": " is", "timestamp": null}
data: {"done": true}
```

### GET /chats/{chat_id}/messages
Get chat message history.

**Response (200):**
```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "What is the main topic?",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "The main topic is...",
      "metadata": {
        "timestamps": [12.5, 45.2]
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## Playback Endpoints

### GET /playback/{document_id}/segment
Get playback segment for a timestamp.

**Query Params:**
- `timestamp`: Float (required)
- `duration`: Float (optional, default: 30)

**Response (200):**
```json
{
  "start_time": 0.0,
  "end_time": 30.0,
  "transcript": "Segment transcript text...",
  "s3_url": "https://s3.amazonaws.com/..."
}
```

---

## Summary Endpoints

### GET /summaries/{document_id}
Get document summary.

**Response (200):**
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "content": "Summary text...",
  "summary_type": "auto",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### POST /summaries/{document_id}/regenerate
Regenerate document summary.

**Response (201):**
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "content": "New summary text...",
  "summary_type": "on_demand",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## Health Endpoints

### GET /health
Health check.

**Response (200):**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "faiss": "loaded"
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "detail": "Validation error"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Not enough permissions"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

- Auth endpoints: 10 requests/minute
- Upload: 5 requests/minute
- Chat: 100 requests/minute
- Other endpoints: 60 requests/minute

Rate limits are enforced per user using Redis.
