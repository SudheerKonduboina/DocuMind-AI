"""
Migrate video transcript from SQLite to PostgreSQL and rebuild FAISS index.
"""
import sqlite3
import psycopg2
from psycopg2.extras import register_uuid
import uuid
from datetime import datetime

# Configuration
SQLITE_DB = r"c:\Users\kondu\CascadeProjects\ai-doc-qa-app\demo_v2.db"
DOCUMENT_ID = "f16924b9a74b40268c914f6f79b78a76"

# PostgreSQL configuration (update with your actual credentials)
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB = "ai_doc_qa"
PG_USER = "user"
PG_PASSWORD = "password"

def get_sqlite_transcript(db_path, document_id):
    """Get transcript from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get transcript
    cursor.execute(
        "SELECT id, document_id, full_text, language, duration_seconds, created_at FROM transcripts WHERE document_id = ?",
        (document_id,)
    )
    transcript = cursor.fetchone()
    
    if not transcript:
        print(f"No transcript found for document {document_id}")
        return None, []
    
    transcript_data = {
        'id': transcript[0],
        'document_id': transcript[1],
        'full_text': transcript[2],
        'language': transcript[3],
        'duration_seconds': transcript[4],
        'created_at': transcript[5]
    }
    
    # Get segments
    cursor.execute(
        "SELECT id, transcript_id, content, start_time, end_time, created_at FROM transcript_segments WHERE transcript_id = ?",
        (transcript_data['id'],)
    )
    segments = cursor.fetchall()
    
    segments_data = [
        {
            'id': seg[0],
            'transcript_id': seg[1],
            'content': seg[2],
            'start_time': seg[3],
            'end_time': seg[4],
            'created_at': seg[5]
        }
        for seg in segments
    ]
    
    conn.close()
    
    print(f"Found transcript with {len(segments_data)} segments")
    return transcript_data, segments_data

def migrate_to_postgresql(transcript_data, segments_data):
    """Migrate transcript to PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cursor = conn.cursor()
        
        # Insert transcript
        cursor.execute(
            """INSERT INTO transcripts (id, document_id, full_text, language, duration_seconds, created_at)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO NOTHING""",
            (
                transcript_data['id'],
                transcript_data['document_id'],
                transcript_data['full_text'],
                transcript_data['language'],
                transcript_data['duration_seconds'],
                transcript_data['created_at']
            )
        )
        print(f"Inserted transcript {transcript_data['id']}")
        
        # Insert segments
        for seg in segments_data:
            cursor.execute(
                """INSERT INTO transcript_segments (id, transcript_id, content, start_time, end_time, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (id) DO NOTHING""",
                (
                    seg['id'],
                    seg['transcript_id'],
                    seg['content'],
                    seg['start_time'],
                    seg['end_time'],
                    seg['created_at']
                )
            )
        
        conn.commit()
        print(f"Inserted {len(segments_data)} segments")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error migrating to PostgreSQL: {e}")
        return False

def main():
    print("=" * 60)
    print("Transcript Migration Script")
    print("=" * 60)
    
    # Step 1: Get transcript from SQLite
    print("\nStep 1: Fetching transcript from SQLite...")
    transcript_data, segments_data = get_sqlite_transcript(SQLITE_DB, DOCUMENT_ID)
    
    if not transcript_data:
        print("No transcript found. Exiting.")
        return
    
    # Step 2: Migrate to PostgreSQL
    print("\nStep 2: Migrating to PostgreSQL...")
    print("Note: Please update PostgreSQL credentials in the script before running.")
    print("Current config: host=localhost, port=5432, db=ai_doc_qa, user=user, password=password")
    
    # Uncomment the following line after updating credentials:
    # success = migrate_to_postgresql(transcript_data, segments_data)
    
    # For now, we'll just print what would be migrated
    print("\nWould migrate:")
    print(f"  Transcript ID: {transcript_data['id']}")
    print(f"  Document ID: {transcript_data['document_id']}")
    print(f"  Segments: {len(segments_data)}")
    
    print("\n" + "=" * 60)
    print("Please update PostgreSQL credentials in the script and uncomment the migration line.")
    print("=" * 60)

if __name__ == "__main__":
    main()
