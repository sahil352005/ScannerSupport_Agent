import streamlit as st
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from typing import List, Dict, Any
from config import SUPABASE_URL, SUPABASE_KEY, EMBEDDING_MODEL, TOP_K_RESULTS
import os

class EmbeddingService:
    def __init__(self):
        # Lazy-load the embedding model
        if 'embedder' not in st.session_state:
            with st.spinner('Loading embedding model...'):
                st.session_state.embedder = SentenceTransformer(EMBEDDING_MODEL)
        
        # Initialize Supabase client once
        if 'supabase_client' not in st.session_state:
            st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        self.embedder = st.session_state.embedder
        self.supabase: Client = st.session_state.supabase_client

    def embed_query(self, query: str) -> List[float]:
        """Generate embeddings for a query."""
        # Cache query embeddings to avoid recomputing
        cache_key = f"embed_{query}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
            
        embedding = self.embedder.encode([query])[0].tolist()
        st.session_state[cache_key] = embedding
        return embedding

    def search_documents(self, query_embedding: List[float], top_k: int = TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """Search for relevant documents using vector similarity."""
        try:
            response = self.supabase.rpc(
                "match_documents",
                {"query_embedding": query_embedding, "match_count": top_k}
            ).execute()
            
            if hasattr(response, 'data'):
                return response.data
            return []
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []

    def format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format the sources for display."""
        if not sources:
            return ""
        files = set([s.get("source") for s in sources if s.get("source")])
        return "Sources: " + ", ".join(files)

    @staticmethod
    def is_comparison_query(query: str) -> bool:
        """Check if the query is asking for a comparison."""
        q = query.lower()
        return any(word in q for word in ["compare", "comparison", "vs", "versus"]) 