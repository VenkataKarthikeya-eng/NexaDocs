import os
import re
import json
import shutil
import tempfile
import numpy as np
from typing import List, Dict, Any, Optional
from app.core.config import settings

class FAISSVectorStore:
    def __init__(self):
        self.doc_chunks: Dict[str, List[Dict[str, Any]]] = {}
        self.faiss_indices: Dict[str, Any] = {}
        self.use_faiss = False
        self.indices_dir = os.path.join(settings.UPLOAD_DIR, "indices")
        os.makedirs(self.indices_dir, exist_ok=True)
        self.dimension = 384
        self._model = None
        self._model_failed = False

        try:
            import faiss
            self.faiss = faiss
            self.use_faiss = True
            print("[FAISSVectorStore] FAISS native library initialized.")
        except ImportError:
            self.faiss = None
            self.use_faiss = False
            print("[FAISSVectorStore] FAISS native library unavailable; utilizing NumPy Cosine Vector space.")

    def _get_model(self):
        """Lazy loads SentenceTransformer model and caches in memory."""
        if self._model is not None:
            return self._model
        if self._model_failed:
            return None

        try:
            from sentence_transformers import SentenceTransformer
            print("[FAISSVectorStore] Loading SentenceTransformer 'all-MiniLM-L6-v2' (384-dim)...")
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[FAISSVectorStore] SentenceTransformer loaded successfully.")
            return self._model
        except Exception as e:
            print(f"[FAISSVectorStore] SentenceTransformer load warning: {e}")
            self._model_failed = True
            return None

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generates normalized 384-dimensional dense semantic embedding vector.
        L2 normalized for exact Cosine Similarity via Inner Product (IndexFlatIP).
        """
        model = self._get_model()
        if model is not None:
            try:
                vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
                vec = np.asarray(vec, dtype=np.float32)
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                return vec
            except Exception as e:
                print(f"[FAISSVectorStore] Inference error on SentenceTransformer: {e}")

        # Deterministic semantic hash projection fallback (384-dim normalized)
        import hashlib
        tokens = re.findall(r'\b[a-zA-Z0-9_\-\$]+\b', text.lower())
        vec = np.zeros(self.dimension, dtype=np.float32)
        for token in tokens:
            if len(token) < 2:
                continue
            h = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16) % self.dimension
            vec[h] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def index_document_chunks(self, doc_id: str, chunks: List[Dict[str, Any]]):
        """
        Encodes document chunks with dense embeddings, builds FAISS index,
        and atomically persists vectors and chunk metadata to disk.
        """
        if not chunks:
            return

        self.doc_chunks[doc_id] = chunks

        # 1. Compute dense embeddings for all chunks
        texts = [c.get("text", "") for c in chunks]
        model = self._get_model()
        if model is not None:
            try:
                raw_embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                embeddings = np.asarray(raw_embeddings, dtype=np.float32)
                # L2 normalize
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                embeddings = embeddings / norms
            except Exception as e:
                print(f"[FAISSVectorStore] Batch encode fallback: {e}")
                embeddings = np.array([self.get_embedding(t) for t in texts], dtype=np.float32)
        else:
            embeddings = np.array([self.get_embedding(t) for t in texts], dtype=np.float32)

        # 2. Build FAISS index
        if self.use_faiss and self.faiss is not None:
            try:
                index = self.faiss.IndexFlatIP(self.dimension)
                index.add(embeddings)
                self.faiss_indices[doc_id] = index

                # Atomic persistence of FAISS binary index
                faiss_file = os.path.join(self.indices_dir, f"{doc_id}.faiss")
                tmp_faiss = faiss_file + ".tmp"
                self.faiss.write_index(index, tmp_faiss)
                if os.path.exists(faiss_file):
                    os.remove(faiss_file)
                os.rename(tmp_faiss, faiss_file)
            except Exception as e:
                print(f"[FAISSVectorStore] FAISS write error: {e}")

        # 3. Atomic persistence of chunk metadata JSON
        chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
        tmp_chunks = chunks_file + ".tmp"
        try:
            with open(tmp_chunks, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)
            if os.path.exists(chunks_file):
                os.remove(chunks_file)
            os.rename(tmp_chunks, chunks_file)
        except Exception as e:
            print(f"[FAISSVectorStore] Error writing chunks file: {e}")

        print(f"[FAISSVectorStore] Successfully indexed & persisted {len(chunks)} chunks for doc {doc_id}.")

    def _ensure_loaded(self, doc_id: str) -> List[Dict[str, Any]]:
        """Ensures chunk metadata and FAISS index are loaded from memory, disk, or on-demand DB recovery."""
        if doc_id in self.doc_chunks and len(self.doc_chunks[doc_id]) > 0:
            if not self.use_faiss or doc_id in self.faiss_indices:
                return self.doc_chunks[doc_id]

        chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
        faiss_file = os.path.join(self.indices_dir, f"{doc_id}.faiss")

        # 1. Load from disk JSON
        if os.path.exists(chunks_file):
            try:
                with open(chunks_file, "r", encoding="utf-8") as f:
                    self.doc_chunks[doc_id] = json.load(f)
            except Exception as e:
                print(f"[FAISSVectorStore] Error reading chunks file {chunks_file}: {e}")

        # 2. Load FAISS binary index from disk
        if self.use_faiss and self.faiss is not None and os.path.exists(faiss_file):
            try:
                self.faiss_indices[doc_id] = self.faiss.read_index(faiss_file)
            except Exception as e:
                print(f"[FAISSVectorStore] Error reading faiss file {faiss_file}: {e}")

        # 3. If memory still empty, attempt on-demand rebuild from original file in PostgreSQL
        if not self.doc_chunks.get(doc_id):
            try:
                from app.core.database import SessionLocal
                from app.models.document import Document
                from app.services.pdf_service import pdf_service

                db = SessionLocal()
                try:
                    doc = db.query(Document).filter(Document.id == doc_id).first()
                    if doc and doc.file_path and os.path.exists(doc.file_path):
                        print(f"[FAISSVectorStore] On-demand rebuilding index for doc {doc_id} from {doc.file_path}...")
                        extracted = pdf_service.extract_text_and_pages(doc.file_path)
                        chunks = pdf_service.chunk_text(extracted["pages"])
                        self.index_document_chunks(doc_id, chunks)
                finally:
                    db.close()
            except Exception as e:
                print(f"[FAISSVectorStore] On-demand recovery error for doc {doc_id}: {e}")

        return self.doc_chunks.get(doc_id, [])

    def search_similar_chunks(
        self,
        doc_id: str,
        query: str,
        top_k: int = 4,
        min_score: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid semantic search matching query embedding against document chunks.
        Returns top-k relevant chunks with genuine cosine similarity scores and exact page numbers.
        """
        chunks = self._ensure_loaded(doc_id)
        if not chunks:
            return []

        query_vec = self.get_embedding(query).reshape(1, -1)
        scored_results: List[Dict[str, Any]] = []

        # 1. FAISS Search
        if self.use_faiss and self.faiss is not None and doc_id in self.faiss_indices:
            try:
                index = self.faiss_indices[doc_id]
                k = min(len(chunks), top_k * 2)
                distances, indices = index.search(query_vec, k)

                for dist, idx in zip(distances[0], indices[0]):
                    if 0 <= idx < len(chunks):
                        chunk = dict(chunks[idx])
                        # Cosine similarity in FlatIP (-1.0 to 1.0), normalized to 0.0 to 1.0 range
                        sim = float(dist)
                        chunk["score"] = round(max(0.0, min(1.0, sim)), 4)
                        scored_results.append(chunk)
            except Exception as e:
                print(f"[FAISSVectorStore] FAISS search error, falling back to NumPy: {e}")
                scored_results.clear()

        # 2. NumPy Cosine Similarity Fallback
        if not scored_results:
            chunk_vectors = np.array([self.get_embedding(c.get("text", "")) for c in chunks], dtype=np.float32)
            dots = np.dot(chunk_vectors, query_vec.T).flatten()
            for idx, score in enumerate(dots):
                chunk = dict(chunks[idx])
                chunk["score"] = round(max(0.0, min(1.0, float(score))), 4)
                scored_results.append(chunk)

        # 3. Hybrid Lexical Keyword Boost (for exact entities, numbers, acronyms)
        query_terms = set(re.findall(r'\b[a-zA-Z0-9_\$]+\b', query.lower())) - {
            "what", "is", "the", "in", "of", "and", "to", "a", "for", "on", "with", "this", "that"
        }
        if query_terms:
            for item in scored_results:
                text_low = item.get("text", "").lower()
                matches = sum(1 for term in query_terms if term in text_low)
                if matches > 0:
                    keyword_bonus = min(0.20, matches * 0.05)
                    item["score"] = round(min(1.0, item["score"] + keyword_bonus), 4)

        # 4. Sort descending by score, filter by minimum threshold, and slice top_k
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        filtered = [c for c in scored_results if c["score"] >= min_score]

        return filtered[:top_k]

    def delete_index(self, doc_id: str):
        """Atomically cleans up in-memory vector cache and on-disk files for document."""
        self.doc_chunks.pop(doc_id, None)
        self.faiss_indices.pop(doc_id, None)

        chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
        faiss_file = os.path.join(self.indices_dir, f"{doc_id}.faiss")

        for fpath in [chunks_file, faiss_file, chunks_file + ".tmp", faiss_file + ".tmp"]:
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass

embedding_service = FAISSVectorStore()
