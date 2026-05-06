# Demo Walkthrough Script

## Setup Instructions

1. **Start the application**
   ```bash
   docker-compose up -d
   ```
   Wait for all services to be healthy (PostgreSQL, Redis, Backend, Frontend)

2. **Open the application**
   - Navigate to http://localhost
   - Verify the application loads correctly

## Demo Script

### Section 1: Introduction (30 seconds)

**Narrator:** "Welcome to the AI Document & Multimedia Q&A Application. This production-ready platform allows you to upload PDFs, audio, and video files to get AI-powered summaries, transcriptions, and interactive Q&A capabilities."

**Visuals:**
- Show the landing page/login screen
- Highlight the clean, modern UI

### Section 2: User Registration (45 seconds)

**Actions:**
1. Click "Register" in the navigation
2. Fill in registration form:
   - Email: demo@example.com
   - Password: Demo123!
   - Full Name: Demo User
3. Click "Register"
4. Wait for successful registration
5. Automatically redirected to login

**Narrator:** "Let's start by creating a new account. The registration process is simple and secure with JWT-based authentication."

### Section 3: Login (30 seconds)

**Actions:**
1. Enter credentials:
   - Email: demo@example.com
   - Password: Demo123!
2. Click "Login"
3. Wait for successful login
4. Redirected to Dashboard

**Narrator:** "After registration, we log in with our credentials to access the main dashboard."

### Section 4: Dashboard Overview (45 seconds)

**Actions:**
1. Show the dashboard layout
2. Highlight recent documents section
3. Highlight recent chats section
4. Show navigation sidebar

**Narrator:** "The dashboard provides an overview of your recent documents and chat sessions. You can easily navigate to different features using the sidebar."

### Section 5: Document Upload (90 seconds)

**Actions:**
1. Click "Upload" in the sidebar
2. Show the upload interface
3. Drag and drop a sample PDF file (or click to browse)
4. Optionally set a custom title
5. Click "Upload Document"
6. Show upload progress
7. Wait for processing to complete
8. Show success message and redirect to Media Library

**Narrator:** "Now let's upload a document. The application supports PDFs, audio files (MP3, WAV, M4A), and videos (MP4, MOV, AVI) up to 500MB. Simply drag and drop or browse to select your file."

### Section 6: Media Library (60 seconds)

**Actions:**
1. Show the media library grid
2. Demonstrate filtering by file type (PDF, Audio, Video)
3. Show search functionality
4. Click on the uploaded document
5. Show document details

**Narrator:** "The media library organizes all your uploaded files. You can filter by type and search for specific documents. Each card shows the file type, size, upload date, and processing status."

### Section 7: AI Summary Generation (90 seconds)

**Actions:**
1. Click "Generate Summary" on a completed document
2. Show the summary generation progress
3. Display the generated summary
4. Highlight the executive summary format
5. Show regenerate option
6. Demonstrate deleting a summary

**Narrator:** "One of the key features is AI-powered summarization. The application uses OpenAI's GPT models to generate concise, accurate summaries of your documents. You can regenerate summaries if needed."

### Section 8: Interactive Chat (120 seconds)

**Actions:**
1. Click "Chat" in the sidebar
2. Create a new chat session
3. Link it to the uploaded document
4. Ask a question: "What is the main topic of this document?"
5. Show the streaming AI response
6. Ask a follow-up question
7. Show context-aware response
8. Demonstrate chat history
9. Show creating a new chat
10. Show deleting a chat

**Narrator:** "The interactive chat feature allows you to ask questions about your documents. The AI provides context-aware responses by searching through the document content using vector similarity. Responses stream in real-time for a natural conversation experience."

### Section 9: Media Playback (60 seconds)

**Actions:**
1. Upload an audio or video file (if not already done)
2. Wait for transcription to complete
3. Click on the media file in the library
4. Show the media player
5. Demonstrate playback controls (play/pause, skip)
6. Show progress bar and time display
7. Demonstrate seeking

**Narrator:** "For audio and video files, the application provides a built-in media player with full playback controls. The files are automatically transcribed using OpenAI Whisper, enabling transcript synchronization."

### Section 10: Summary & Conclusion (45 seconds)

**Actions:**
1. Return to dashboard
2. Show logout functionality
3. Display the application running smoothly

**Narrator:** "In summary, the AI Document & Multimedia Q&A Application provides a complete solution for document analysis with features including secure authentication, multi-format file support, AI summarization, interactive Q&A, and media playback. The application is production-ready with comprehensive testing, Docker containerization, and AWS deployment capabilities."

## Recording Checklist

### Pre-Recording Setup
- [ ] Application is running locally (docker-compose up -d)
- [ ] All services are healthy (PostgreSQL, Redis, Backend, Frontend)
- [ ] Sample files ready for upload (PDF, audio, video)
- [ ] Screen recording software configured (OBS, Loom, etc.)
- [ ] Microphone tested for audio quality
- [ ] Browser window sized appropriately (1920x1080 recommended)
- [ ] Browser bookmarks bar hidden for clean view
- [ ] Development tools closed

### During Recording
- [ ] Speak clearly and at a moderate pace
- [ ] Use mouse movements to guide viewer attention
- [ ] Wait for loading states to complete before proceeding
- [ ] Highlight key UI elements with cursor
- [ ] Keep narration synchronized with actions
- [ ] Avoid unnecessary clicks or movements
- [ ] Maintain consistent window positioning
- [ ] Check audio levels throughout

### Post-Recording
- [ ] Review recording for audio clarity
- [ ] Check for any lag or stuttering
- [ ] Verify all features were demonstrated
- [ ] Add intro/outro text if needed
- [ ] Add captions/subtitles if required
- [ ] Export in appropriate format (MP4 recommended)
- [ ] Upload to designated platform

### Common Issues to Avoid
- [ ] Don't rush through complex features
- [ ] Don't skip loading states or error handling
- [ ] Don't use placeholder data that looks fake
- [ ] Don't leave sensitive information visible
- [ ] Don't have background noise or distractions
- [ ] Don't use browser extensions that interfere

### Demo Data Preparation
- [ ] Prepare a sample PDF document (5-10 pages)
- [ ] Prepare a sample audio file (1-2 minutes)
- [ ] Prepare a sample video file (1-2 minutes)
- [ ] Ensure files are under 500MB limit
- [ ] Test files upload successfully before recording
- [ ] Have backup files ready in case of issues

### Technical Notes
- Backend API: http://localhost:8000
- Frontend: http://localhost
- API Docs: http://localhost:8000/docs
- Default processing time: 30-60 seconds per file
- Rate limits: 100 requests per minute per user
