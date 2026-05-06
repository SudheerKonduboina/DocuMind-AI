# API Documentation

Base URL: http://localhost:8000

## Auth
- POST /auth/register - Register user
- POST /auth/login - Login
- GET /auth/me - Get current user

## Documents
- POST /documents/upload - Upload file
- GET /documents - List documents
- GET /documents/{id} - Get document
- DELETE /documents/{id} - Delete document

## Chats
- POST /chats - Create chat
- GET /chats - List chats
- GET /chats/{id} - Get chat
- DELETE /chats/{id} - Delete chat
- POST /chats/{id}/messages - Send message (streaming)
- GET /chats/{id}/messages - Get messages

## Summaries
- GET /summaries/{document_id} - Get summary
- POST /summaries/{document_id} - Generate summary
- POST /summaries/{document_id}/regenerate - Regenerate
- DELETE /summaries/{document_id} - Delete

## Media
- GET /media/transcripts/{document_id} - Get transcript
- GET /media/transcripts/{document_id}/segments - Get segments

## Playback
- GET /playback/{document_id}/segment - Get playback segment
- GET /playback/{document_id}/url - Get media URL
