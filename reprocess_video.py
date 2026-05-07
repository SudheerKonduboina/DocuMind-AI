"""
Direct script to reprocess a stuck video document using Whisper.
This bypasses the API and works directly with the SQLite database.
"""

import sqlite3
import whisper
import os
import uuid
from datetime import datetime

# Configuration
DB_PATH = r"c:\Users\kondu\CascadeProjects\ai-doc-qa-app\demo_v2.db"
DOCUMENT_ID = "f16924b9a74b40268c914f6f79b78a76"
UPLOADS_DIR = r"c:\Users\kondu\CascadeProjects\ai-doc-qa-app\backend\uploads"


def get_document_info(db_path, document_id):
    """Get document information from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, user_id, title, file_type, s3_key, file_size, status FROM documents WHERE id = ?",
        (document_id,),
    )
    result = cursor.fetchone()

    conn.close()

    if not result:
        print(f"Document {document_id} not found in database")
        return None

    return {
        "id": result[0],
        "user_id": result[1],
        "title": result[2],
        "file_type": result[3],
        "s3_key": result[4],
        "file_size": result[5],
        "status": result[6],
    }


def find_video_file(document_info):
    """Find the video file in the uploads directory."""
    # The s3_key is typically in format: user_id/filename
    s3_key = document_info["s3_key"]
    filename = s3_key.split("/")[-1] if "/" in s3_key else s3_key

    # Search for the file in uploads directory
    for root, dirs, files in os.walk(UPLOADS_DIR):
        for file in files:
            if file == filename:
                return os.path.join(root, file)

    print(f"Video file not found: {filename}")
    return None


def transcribe_video(video_path, language="en"):
    """Transcribe video using Whisper."""
    print(f"Loading Whisper model...")
    model = whisper.load_model("base")

    print(f"Starting transcription for: {video_path}")
    result = model.transcribe(video_path, language=language)

    print(f"Transcription completed. Segments: {len(result['segments'])}")

    return result


def create_transcript(db_path, document_id, transcription_result):
    """Create transcript and segments in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create transcript record
    transcript_id = str(uuid.uuid4())
    full_text = transcription_result["text"]
    language = "en"
    duration_seconds = (
        int(max(seg["end"] for seg in transcription_result["segments"]))
        if transcription_result["segments"]
        else 0
    )
    created_at = datetime.utcnow().isoformat()

    cursor.execute(
        """INSERT INTO transcripts (id, document_id, full_text, language, duration_seconds, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (transcript_id, document_id, full_text, language, duration_seconds, created_at),
    )

    # Create transcript segments
    segments = transcription_result["segments"]
    for seg in segments:
        segment_id = str(uuid.uuid4())
        content = seg["text"].strip()
        start_time = seg["start"]
        end_time = seg["end"]

        cursor.execute(
            """INSERT INTO transcript_segments (id, transcript_id, content, start_time, end_time, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (segment_id, transcript_id, content, start_time, end_time, created_at),
        )

    conn.commit()
    conn.close()

    print(f"Created transcript {transcript_id} with {len(segments)} segments")
    return transcript_id


def update_document_status(db_path, document_id, status):
    """Update document status in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE documents SET status = ?, updated_at = ? WHERE id = ?",
        (status, datetime.utcnow().isoformat(), document_id),
    )

    conn.commit()
    conn.close()

    print(f"Updated document {document_id} status to: {status}")


def main():
    print("=" * 60)
    print("Direct Video Reprocessing Script")
    print("=" * 60)

    # Step 1: Get document info
    print("\nStep 1: Fetching document info...")
    doc_info = get_document_info(DB_PATH, DOCUMENT_ID)
    if not doc_info:
        return

    print(f"  Document ID: {doc_info['id']}")
    print(f"  Title: {doc_info['title']}")
    print(f"  Type: {doc_info['file_type']}")
    print(f"  Current Status: {doc_info['status']}")
    print(f"  S3 Key: {doc_info['s3_key']}")

    # Step 2: Find video file
    print("\nStep 2: Locating video file...")
    video_path = find_video_file(doc_info)
    if not video_path:
        return

    print(f"  Found: {video_path}")
    print(f"  File size: {os.path.getsize(video_path) / (1024*1024):.2f} MB")

    # Step 3: Transcribe with Whisper
    print("\nStep 3: Transcribing with Whisper...")
    try:
        transcription_result = transcribe_video(video_path)
    except Exception as e:
        print(f"  ERROR: Transcription failed: {e}")
        update_document_status(DB_PATH, DOCUMENT_ID, "failed")
        return

    # Step 4: Create transcript in database
    print("\nStep 4: Creating transcript in database...")
    try:
        create_transcript(DB_PATH, DOCUMENT_ID, transcription_result)
    except Exception as e:
        print(f"  ERROR: Failed to create transcript: {e}")
        update_document_status(DB_PATH, DOCUMENT_ID, "failed")
        return

    # Step 5: Update document status
    print("\nStep 5: Updating document status...")
    update_document_status(DB_PATH, DOCUMENT_ID, "completed")

    print("\n" + "=" * 60)
    print("SUCCESS: Video transcription completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
