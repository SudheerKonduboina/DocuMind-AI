# Demo Checklist

This checklist provides step-by-step instructions for setting up and running the AI Document QA application for demonstration purposes.

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database (or use SQLite for demo)
- Redis server (optional, for caching)
- AWS S3 account (or use local storage for demo)
- xAI API key (Grok) for LLM functionality

## Backend Setup

### 1. Environment Configuration

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=sqlite:///./demo.db  # Use SQLite for demo
SECRET_KEY=your-secret-key-here

# xAI/Grok API
XAI_API_KEY=your-xai-api-key
XAI_MODEL_NAME=grok-beta
XAI_BASE_URL=https://api.x.ai/v1

# AWS S3 (optional - can use local storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1

# Redis (optional)
REDIS_URL=redis://localhost:6379

# File Upload
ALLOWED_FILE_TYPES=pdf,mp3,wav,m4a,mp4,mov,avi
MAX_FILE_SIZE=52428800  # 50MB

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python -c "from database.init_db import init_db; init_db()"
```

### 4. Start Backend Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### 5. Verify Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_provider": "configured"
}
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Demo Scenarios

### Scenario 1: Document Upload and Processing

1. **Upload a PDF Document**
   - Navigate to the upload page
   - Select a PDF file
   - Enter title and description
   - Click upload
   - Verify document appears in the list

2. **Upload an Audio File**
   - Select an MP3 or WAV file
   - Upload the file
   - Wait for transcription to complete
   - View transcript with timestamps

3. **Upload a Video File**
   - Select an MP4 or MOV file
   - Upload the file
   - Wait for transcription
   - View transcript and playback options

### Scenario 2: Chatbot Q&A

1. **Create a Chat**
   - Click "New Chat"
   - Enter chat title
   - Optionally select a document to chat about

2. **Ask Questions**
   - Type a question in the chat interface
   - View the AI response
   - Check if timestamps are included for relevant content
   - Continue the conversation

3. **View Chat History**
   - Navigate to chat list
   - View previous conversations
   - Select a chat to continue

### Scenario 3: Document Summarization

1. **Generate Summary**
   - Select a document from the list
   - Click "Generate Summary"
   - Wait for AI to process
   - View the summary with key points

2. **Compare Summaries**
   - Generate summaries for multiple documents
   - Compare the key points
   - Export summaries if needed

### Scenario 4: Media Playback

1. **Play Audio/Video**
   - Select a media file
   - Click play in the media player
   - Use timeline to navigate
   - View transcript segments synced with playback

2. **Jump to Timestamp**
   - Click on a transcript segment
   - Media player jumps to that timestamp
   - View context around the segment

### Scenario 5: Vector Search

1. **Search Across Documents**
   - Enter a search query
   - View semantic search results
   - Click on results to view context
   - Filter by document type

## API Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@test.pdf" \
  -F "title=Test Document"

# List documents
curl http://localhost:8000/documents

# Create chat
curl -X POST http://localhost:8000/chats \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat", "document_id": null}'

# Send message
curl -X POST http://localhost:8000/chats/{chat_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is this document about?"}'
```

### Using Swagger UI

Navigate to `http://localhost:8000/docs` for interactive API documentation.

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] Health check returns healthy status
- [ ] Document upload works for PDF files
- [ ] Document upload works for audio files
- [ ] Document upload works for video files
- [ ] Transcription completes successfully
- [ ] Chatbot responds to questions
- [ ] Chatbot includes timestamps in responses
- [ ] Summary generation works
- [ ] Media playback works
- [ ] Vector search returns relevant results
- [ ] Frontend loads without errors
- [ ] Frontend can communicate with backend
- [ ] File size validation works
- [ ] File type validation works
- [ ] Rate limiting is enforced (if enabled)

## Troubleshooting

### Backend Issues

**Issue**: Database connection error
- **Solution**: Check DATABASE_URL in .env, ensure database is running

**Issue**: xAI API error
- **Solution**: Verify XAI_API_KEY is correct and has credits

**Issue**: File upload fails
- **Solution**: Check MAX_FILE_SIZE and ALLOWED_FILE_TYPES in .env

**Issue**: Transcription fails
- **Solution**: Ensure Whisper model is downloaded, check file format

### Frontend Issues

**Issue**: Cannot connect to backend
- **Solution**: Check CORS_ORIGINS in .env, ensure backend is running

**Issue**: Media player not working
- **Solution**: Check browser console for errors, verify file format

**Issue**: Chat not responding
- **Solution**: Check backend logs, verify LLM API is configured

## Performance Tips

1. **Use SQLite for demo**: Faster setup, no external dependencies
2. **Disable rate limiting**: Set RATE_LIMIT_ENABLED=false for demo
3. **Use smaller files**: Upload smaller files for faster processing
4. **Cache responses**: Enable Redis for better performance
5. **Pre-download models**: Ensure Whisper model is downloaded before demo

## Security Notes for Demo

- Use demo-specific API keys
- Don't expose production credentials
- Use test database, not production
- Enable rate limiting if demo is public
- Monitor resource usage during demo
- Clean up demo data after presentation

## Cleanup

After demo:

```bash
# Stop servers
# Ctrl+C in backend and frontend terminals

# Remove demo database
rm backend/demo.db

# Remove uploaded files
rm -rf backend/uploads/*

# Clear Redis cache (if used)
redis-cli FLUSHALL
```
