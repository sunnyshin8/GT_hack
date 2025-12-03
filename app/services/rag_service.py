"""
RAG (Retrieval Augmented Generation) service for document embedding and retrieval.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    cosine_similarity = None
    SKLEARN_AVAILABLE = False

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """RAG service for document embedding and semantic search."""
    
    def __init__(self):
        """Initialize the RAG service with embedding model."""
        self.model = None
        self.embedding_cache: Dict[str, List[float]] = {}
        
    async def initialize(self):
        """Initialize the embedding model."""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("sentence-transformers not available, RAG service will be limited")
                return
            self.model = SentenceTransformer(settings.embedding_model)
            logger.info(f"RAG service initialized with model: {settings.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a text string."""
        if not self.model:
            raise RuntimeError("RAG service not initialized")
        
        # Check cache first
        cache_key = hash(text)
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            embedding = self.model.encode(text).tolist()
            
            # Cache the embedding
            if len(self.embedding_cache) < 1000:  # Prevent memory bloat
                self.embedding_cache[cache_key] = embedding
                
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not self.model:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.error("sentence-transformers not available, cannot generate embeddings")
                return []
            raise RuntimeError("RAG service not initialized")
        
        try:
            embeddings = self.model.encode(texts).tolist()
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return []
            raise
    
    def calculate_similarity(
        self,
        query_embedding: List[float], 
        document_embeddings: List[List[float]]
    ) -> List[float]:
        """Calculate cosine similarity between query and document embeddings."""
        try:
            if not SKLEARN_AVAILABLE:
                logger.warning("sklearn not available, using basic similarity calculation")
                # Basic dot product similarity as fallback
                query_vec = np.array(query_embedding)
                similarities = []
                for doc_embedding in document_embeddings:
                    doc_vec = np.array(doc_embedding)
                    similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
                    similarities.append(similarity)
                return similarities
            
            query_vec = np.array(query_embedding).reshape(1, -1)
            doc_vecs = np.array(document_embeddings)
            
            similarities = cosine_similarity(query_vec, doc_vecs)[0]
            return similarities.tolist()
        except Exception as e:
            logger.error(f"Failed to calculate similarities: {e}")
            return []
    
    def retrieve_relevant_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve the most relevant documents for a query.
        
        Args:
            query: The query text
            documents: List of documents with 'content' and 'embedding' keys
            top_k: Number of top results to return
            
        Returns:
            List of (document, similarity_score) tuples
        """
        if not documents:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Extract document embeddings
            doc_embeddings = []
            valid_docs = []
            
            for doc in documents:
                if doc.get('embedding'):
                    doc_embeddings.append(doc['embedding'])
                    valid_docs.append(doc)
                else:
                    # Generate embedding if missing
                    embedding = self.embed_text(doc.get('content', ''))
                    doc_embeddings.append(embedding)
                    doc['embedding'] = embedding
                    valid_docs.append(doc)
            
            if not doc_embeddings:
                return []
            
            # Calculate similarities
            similarities = self.calculate_similarity(query_embedding, doc_embeddings)
            
            # Combine documents with scores and sort
            results = list(zip(valid_docs, similarities))
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Filter by similarity threshold and return top-k
            filtered_results = [
                (doc, score) for doc, score in results 
                if score >= settings.similarity_threshold
            ]
            
            return filtered_results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant documents: {e}")
            return []
    
    def format_rag_context(
        self, 
        relevant_docs: List[Tuple[Dict[str, Any], float]]
    ) -> str:
        """Format retrieved documents into context for the language model."""
        if not relevant_docs:
            return ""
        
        context_parts = []
        for i, (doc, score) in enumerate(relevant_docs, 1):
            doc_type = doc.get('doc_type', 'document')
            content = doc.get('content', '')
            
            context_parts.append(
                f"[Document {i}] ({doc_type}, relevance: {score:.2f})\n{content}\n"
            )
        
        return "\n".join(context_parts)


# Global RAG service instance
rag_service = RAGService()