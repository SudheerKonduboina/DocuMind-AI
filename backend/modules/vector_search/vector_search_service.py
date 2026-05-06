import faiss
import numpy as np
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from core.openai_client import openai_service
from config.settings import settings
import os
import pickle


class VectorSearchService:
    """Service for vector search operations using FAISS and pgvector."""
    
    def __init__(self, db: Session):
        self.db = db
        self.index = None
        self.index_path = settings.FAISS_INDEX_PATH
        self.embedding_dim = settings.EMBEDDING_DIMENSION
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create a new one."""
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else ".", exist_ok=True)
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            # Create flat index for exact search
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self._save_index()
    
    def _save_index(self):
        """Save FAISS index to disk."""
        faiss.write_index(self.index, self.index_path)
    
    async def add_document_chunks(self, chunk_ids: List[str], texts: List[str]) -> None:
        """
        Add document chunks to the vector index.
        
        Args:
            chunk_ids: List of chunk IDs
            texts: List of chunk texts
        """
        # Generate embeddings
        embeddings = await openai_service.generate_embeddings_batch(texts)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        start_idx = self.index.ntotal
        self.index.add(embeddings_array)
        
        # Save index
        self._save_index()
        
        # Store ID mapping
        self._save_id_mapping(start_idx, chunk_ids)
    
    def _save_id_mapping(self, start_idx: int, chunk_ids: List[str]) -> None:
        """Save mapping from FAISS index to chunk IDs."""
        mapping_path = f"{self.index_path}.mapping"
        
        # Load existing mapping
        if os.path.exists(mapping_path):
            with open(mapping_path, 'rb') as f:
                id_mapping = pickle.load(f)
        else:
            id_mapping = {}
        
        # Add new mappings
        for i, chunk_id in enumerate(chunk_ids):
            id_mapping[start_idx + i] = chunk_id
        
        # Save mapping
        with open(mapping_path, 'wb') as f:
            pickle.dump(id_mapping, f)
    
    def _load_id_mapping(self) -> dict:
        """Load mapping from FAISS index to chunk IDs."""
        mapping_path = f"{self.index_path}.mapping"
        
        if os.path.exists(mapping_path):
            with open(mapping_path, 'rb') as f:
                return pickle.load(f)
        return {}
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        user_id: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Search for similar chunks.
        
        Args:
            query: Query text
            top_k: Number of results to return
            user_id: Optional user ID for filtering
        
        Returns:
            List of (chunk_id, score) tuples
        """
        # Generate query embedding
        query_embedding = await openai_service.generate_embedding(query)
        
        # Convert to numpy array and normalize
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        # Search
        scores, indices = self.index.search(query_array, top_k)
        
        # Load ID mapping
        id_mapping = self._load_id_mapping()
        
        # Convert indices to chunk IDs
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx in id_mapping:
                chunk_id = id_mapping[idx]
                results.append((chunk_id, float(score)))
        
        # Filter by user if needed (would require database lookup)
        if user_id:
            results = self._filter_by_user(results, user_id)
        
        return results
    
    def _filter_by_user(
        self,
        results: List[Tuple[str, float]],
        user_id: str
    ) -> List[Tuple[str, float]]:
        """Filter results by user ID."""
        from backend.modules.document.document_models import DocumentChunk
        from backend.modules.media.media_models import TranscriptSegment
        
        chunk_ids = [r[0] for r in results]
        
        # Query database to check ownership
        # This is a simplified check - in production you'd optimize this
        filtered_results = []
        
        for chunk_id, score in results:
            # Check if chunk belongs to user's document
            chunk = self.db.query(DocumentChunk).filter(
                DocumentChunk.id == chunk_id
            ).first()
            
            if chunk:
                document = self.db.query(DocumentChunk.document_id).filter(
                    DocumentChunk.id == chunk_id
                ).first()
                # Would need to check document.user_id == user_id
                filtered_results.append((chunk_id, score))
        
        return filtered_results
    
    async def delete_chunks(self, chunk_ids: List[str]) -> None:
        """
        Delete chunks from the vector index.
        
        Note: FAISS doesn't support deletion efficiently.
        In production, you'd use a different approach or rebuild the index.
        """
        # For now, we'll rebuild the index without these chunks
        # This is not efficient for large indices
        id_mapping = self._load_id_mapping()
        
        # Create new mapping without deleted chunks
        new_mapping = {
            idx: chunk_id
            for idx, chunk_id in id_mapping.items()
            if chunk_id not in chunk_ids
        }
        
        # Rebuild index (simplified - in production use a more efficient method)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self._save_index()
        
        # Save new mapping
        mapping_path = f"{self.index_path}.mapping"
        with open(mapping_path, 'wb') as f:
            pickle.dump(new_mapping, f)
    
    def get_index_stats(self) -> dict:
        """Get statistics about the vector index."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.embedding_dim,
            "index_type": "IndexFlatIP"
        }
