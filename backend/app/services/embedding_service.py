import os
import re
import json
import numpy as np
from typing import List, Dict, Any
from app.core.config import settings

class FAISSVectorStore:
    def __init__(self):
        self.doc_chunks = {} # doc_id -> list of chunk dicts
        self.use_faiss = False
        self.faiss_indices = {} # doc_id -> faiss index
        self.indices_dir = os.path.join(settings.UPLOAD_DIR, "indices")
        os.makedirs(self.indices_dir, exist_ok=True)
        
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
        """Indexes document text chunks into FAISS vector space and persists to disk."""
        self.doc_chunks[doc_id] = chunks
        
        if not chunks:
            return

        # 1. Persist chunks metadata to disk
        chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
        try:
            with open(chunks_file, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False)
        except Exception as e:
            print(f"[FAISSVectorStore] Error writing chunks file: {e}")

        # 2. Build embeddings
        embeddings = np.array([self._get_embedding(c["text"]) for c in chunks], dtype=np.float32)

        # 3. Build & persist FAISS index
        if self.use_faiss:
            try:
                dimension = embeddings.shape[1]
                index = self.faiss.IndexFlatIP(dimension) # Inner product similarity
                index.add(embeddings)
                self.faiss_indices[doc_id] = index
                
                faiss_file = os.path.join(self.indices_dir, f"{doc_id}.faiss")
                self.faiss.write_index(index, faiss_file)
                print(f"[FAISSVectorStore] Indexed and persisted {len(chunks)} chunks in FAISS for doc {doc_id}.")
                return
            except Exception as e:
                print(f"[FAISSVectorStore] FAISS indexing fallback: {e}")

    def _ensure_loaded(self, doc_id: str) -> List[Dict[str, Any]]:
        """Ensures chunks and FAISS index are loaded into memory from disk or on-demand recovery."""
        if doc_id in self.doc_chunks and (not self.use_faiss or doc_id in self.faiss_indices):
            return self.doc_chunks[doc_id]

        chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
        faiss_file = os.path.join(self.indices_dir, f"{doc_id}.faiss")

        # Load chunks from disk
        if os.path.exists(chunks_file):
            try:
                with open(chunks_file, "r", encoding="utf-8") as f:
                    self.doc_chunks[doc_id] = json.load(f)
            except Exception as e:
                print(f"[FAISSVectorStore] Error reading chunks file {chunks_file}: {e}")

        # Load FAISS index from disk
        if self.use_faiss and os.path.exists(faiss_file):
            try:
                self.faiss_indices[doc_id] = self.faiss.read_index(faiss_file)
            except Exception as e:
                print(f"[FAISSVectorStore] Error reading faiss file {faiss_file}: {e}")

        # If still not loaded, on-demand rebuild if file exists in DB
        if not self.doc_chunks.get(doc_id):
            try:
                from app.core.database import SessionLocal
                from app.models.document import Document
                from app.services.pdf_service import pdf_service

                db = SessionLocal()
                try:
                    doc = db.query(Document).filter(Document.id == doc_id).first()
                    if doc and os.path.exists(doc.file_path):
                        extracted = pdf_service.extract_text_and_pages(doc.file_path)
                        chunks = pdf_service.chunk_text(extracted["pages"])
                        self.index_document_chunks(doc_id, chunks)
                finally:
                    db.close()
            except Exception as e:
                print(f"[FAISSVectorStore] On-demand indexing error: {e}")

        return self.doc_chunks.get(doc_id, [])

    def delete_index(self, doc_id: str):
        """Removes in-memory and on-disk index files for a document."""
        self.doc_chunks.pop(doc_id, None)
        self.faiss_indices.pop(doc_id, None)
        chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
        faiss_file = os.path.join(self.indices_dir, f"{doc_id}.faiss")
        if os.path.exists(chunks_file):
            try:
                os.remove(chunks_file)
            except Exception:
                pass
        if os.path.exists(faiss_file):
            try:
                os.remove(faiss_file)
            except Exception:
                pass

    def search_similar_chunks(self, doc_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant chunks matching query embedding."""
        chunks = self._ensure_loaded(doc_id)
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
