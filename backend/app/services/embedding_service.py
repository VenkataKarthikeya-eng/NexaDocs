import re
import numpy as np
from typing import List, Dict, Any

class FAISSVectorStore:
    def __init__(self):
        self.doc_chunks = {} # doc_id -> list of chunk dicts
        self.use_faiss = False
        self.faiss_indices = {} # doc_id -> faiss index
        
        try:
            import faiss
            self.faiss = faiss
            self.use_faiss = True
            print("[FAISSVectorStore] FAISS C++ library loaded successfully.")
        except ImportError:
            print("[FAISSVectorStore] FAISS native library uninstalled; using lightweight NumPy Cosine Vector engine.")

    def _get_embedding(self, text: str, dim: int = 384) -> np.ndarray:
        """Generates normalized vector embedding representation for text chunk."""
        tokens = re.findall(r'\w+', text.lower())
        vec = np.zeros(dim, dtype=np.float32)
        for idx, token in enumerate(tokens):
            val = sum(ord(c) for c in token) % 100 / 100.0
            vec[idx % dim] += val + 0.1
            
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def index_document_chunks(self, doc_id: str, chunks: List[Dict[str, Any]]):
        """Indexes document text chunks into FAISS vector space."""
        self.doc_chunks[doc_id] = chunks
        
        if not chunks:
            return

        embeddings = np.array([self._get_embedding(c["text"]) for c in chunks], dtype=np.float32)

        if self.use_faiss:
            try:
                dimension = embeddings.shape[1]
                index = self.faiss.IndexFlatIP(dimension) # Inner product similarity
                index.add(embeddings)
                self.faiss_indices[doc_id] = index
                print(f"[FAISSVectorStore] Indexed {len(chunks)} chunks in FAISS for doc {doc_id}.")
                return
            except Exception as e:
                print(f"[FAISSVectorStore] FAISS indexing fallback: {e}")

    def search_similar_chunks(self, doc_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant chunks matching query embedding."""
        chunks = self.doc_chunks.get(doc_id, [])
        if not chunks:
            return []

        query_vec = self._get_embedding(query).reshape(1, -1)

        if self.use_faiss and doc_id in self.faiss_indices:
            try:
                index = self.faiss_indices[doc_id]
                distances, indices = index.search(query_vec, min(top_k, len(chunks)))
                matched = []
                for idx in indices[0]:
                    if 0 <= idx < len(chunks):
                        matched.append(chunks[idx])
                return matched
            except Exception as e:
                print(f"[FAISSVectorStore] FAISS search fallback: {e}")

        # NumPy Cosine Vector similarity fallback
        chunk_embeddings = np.array([self._get_embedding(c["text"]) for c in chunks], dtype=np.float32)
        scores = np.dot(chunk_embeddings, query_vec.T).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [chunks[i] for i in top_indices]

embedding_service = FAISSVectorStore()
