"""
Build FAISS index from transcript segments in SQLite database.
"""
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle
import os

# Configuration
SQLITE_DB = r"c:\Users\kondu\CascadeProjects\ai-doc-qa-app\demo_v2.db"
DOCUMENT_ID = "f16924b9a74b40268c914f6f79b78a76"
FAISS_INDEX_PATH = r"c:\Users\kondu\CascadeProjects\ai-doc-qa-app\data\faiss_index"

def get_transcript_segments(db_path, document_id):
    """Get transcript segments from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get transcript
    cursor.execute(
        "SELECT id FROM transcripts WHERE document_id = ?",
        (document_id,)
    )
    transcript = cursor.fetchone()
    
    if not transcript:
        print(f"No transcript found for document {document_id}")
        return []
    
    transcript_id = transcript[0]
    
    # Get segments
    cursor.execute(
        "SELECT id, content FROM transcript_segments WHERE transcript_id = ? ORDER BY start_time",
        (transcript_id,)
    )
    segments = cursor.fetchall()
    
    conn.close()
    
    print(f"Found {len(segments)} segments")
    return segments

def build_faiss_index(segments):
    """Build FAISS index from transcript segments."""
    # Load sentence transformer model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    print("Generating embeddings...")
    texts = [seg[1] for seg in segments]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings, dtype=np.float32)
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings_array)
    
    # Create FAISS index
    print("Creating FAISS index...")
    embedding_dim = embeddings_array.shape[1]
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(embeddings_array)
    
    # Save index
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH) if os.path.dirname(FAISS_INDEX_PATH) else ".", exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"FAISS index saved to {FAISS_INDEX_PATH}")
    
    # Save ID mapping
    segment_ids = [seg[0] for seg in segments]
    id_mapping = {i: seg_id for i, seg_id in enumerate(segment_ids)}
    
    mapping_path = f"{FAISS_INDEX_PATH}.mapping"
    with open(mapping_path, 'wb') as f:
        pickle.dump(id_mapping, f)
    print(f"ID mapping saved to {mapping_path}")
    
    print(f"Index contains {index.ntotal} vectors with dimension {embedding_dim}")

def main():
    print("=" * 60)
    print("FAISS Index Builder for Transcript Segments")
    print("=" * 60)
    
    # Step 1: Get transcript segments
    print("\nStep 1: Fetching transcript segments...")
    segments = get_transcript_segments(SQLITE_DB, DOCUMENT_ID)
    
    if not segments:
        print("No segments found. Exiting.")
        return
    
    # Step 2: Build FAISS index
    print("\nStep 2: Building FAISS index...")
    build_faiss_index(segments)
    
    print("\n" + "=" * 60)
    print("FAISS index built successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
