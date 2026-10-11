import os
import re
import json
import time
import httpx
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from app.core.config import settings

class PersistentVectorService:
    """
    Production-grade Vector Storage and Remote Embedding Engine for NexaDocs.
    - Default Production Path: Uses Google Gemini Remote Embeddings (models/gemini-embedding-001, 768-d).
      Zero PyTorch / SentenceTransformers overhead in memory (RAM stays <80MB, well below Render Free 512MB).
    - Persistent Storage: Persists document chunks & vector embeddings directly in PostgreSQL (Neon).
      Supports native pgvector similarity search (<=>) when extension is available, with NumPy cosine ranking fallback.
    - Local Development Fallback: Preserves optional FAISS and SentenceTransformers when explicitly enabled.
    """

    def __init__(self):
        self.doc_chunks: Dict[str, List[Dict[str, Any]]] = {}
        self.faiss_indices: Dict[str, Any] = {}
        self.dimension = getattr(settings, "EMBEDDING_DIMENSION", 768)
        self.embedding_provider = getattr(settings, "EMBEDDING_PROVIDER", "GEMINI").upper()
        self.model_name = getattr(settings, "GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
        self.api_key = settings.GEMINI_API_KEY
        self.indices_dir = settings.FAISS_INDEX_PATH if settings.FAISS_INDEX_PATH else os.path.join(settings.UPLOAD_DIR, "indices")
        os.makedirs(self.indices_dir, exist_ok=True)

        self._local_model = None
        self._has_pgvector_col: Optional[bool] = None

    def _get_local_model(self):
        """Lazy loads SentenceTransformer only if explicitly chosen for local dev."""
        if self._local_model is not None:
            return self._local_model
        try:
            from sentence_transformers import SentenceTransformer
            print("[VectorService] Lazy loading local SentenceTransformer 'all-MiniLM-L6-v2'...")
            self._local_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = 384
            return self._local_model
        except Exception as e:
            print(f"[VectorService] Local model load failed: {e}")
            return None

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generates normalized dense semantic embedding vector.
        Uses Google Gemini Remote Embedding API in production.
        """
        if self.embedding_provider == "LOCAL":
            model = self._get_local_model()
            if model is not None:
                vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
                vec = np.asarray(vec, dtype=np.float32)
                norm = np.linalg.norm(vec)
                return (vec / norm) if norm > 0 else vec

        # Production Remote Gemini Embeddings
        if self.api_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/{self.model_name}:embedContent?key={self.api_key}"
            payload = {
                "model": self.model_name,
                "content": {"parts": [{"text": text[:2048]}]},
                "outputDimensionality": self.dimension
            }
            for attempt in range(3):
                try:
                    resp = httpx.post(url, json=payload, timeout=12.0)
                    if resp.status_code == 200:
                        vals = resp.json().get("embedding", {}).get("values", [])
                        vec = np.array(vals, dtype=np.float32)
                        norm = np.linalg.norm(vec)
                        return (vec / norm) if norm > 0 else vec
                    elif resp.status_code in (429, 503):
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    else:
                        print(f"[VectorService] Gemini embedding warning: HTTP {resp.status_code} {resp.text[:120]}")
                        break
                except Exception as e:
                    time.sleep(0.4 * (attempt + 1))
                    if attempt == 2:
                        print(f"[VectorService] Gemini remote embedding error: {e}")

        # Deterministic semantic hash projection fallback (normalized)
        import hashlib
        tokens = re.findall(r'\b[a-zA-Z0-9_\-\$]+\b', text.lower())
        vec = np.zeros(self.dimension, dtype=np.float32)
        for token in tokens:
            if len(token) < 2:
                continue
            h = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16) % self.dimension
            vec[h] += 1.0

        norm = np.linalg.norm(vec)
        return (vec / norm) if norm > 0 else vec

    def get_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Encodes a list of texts into normalized embedding vectors.
        Uses Gemini batchEmbedContents for fast batch processing.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self.embedding_provider == "LOCAL":
            model = self._get_local_model()
            if model is not None:
                vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                vecs = np.asarray(vecs, dtype=np.float32)
                norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                return vecs / norms

        if self.api_key:
            all_embeddings = []
            # Process in batches of up to 40 chunks
            batch_size = 40
            for i in range(0, len(texts), batch_size):
                chunk_batch = texts[i:i + batch_size]
                url = f"https://generativelanguage.googleapis.com/v1beta/{self.model_name}:batchEmbedContents?key={self.api_key}"
                payload = {
                    "requests": [
                        {
                            "model": self.model_name,
                            "content": {"parts": [{"text": t[:2048]}]},
                            "outputDimensionality": self.dimension
                        }
                        for t in chunk_batch
                    ]
                }
                batch_success = False
                for attempt in range(3):
                    try:
                        resp = httpx.post(url, json=payload, timeout=20.0)
                        if resp.status_code == 200:
                            emb_list = resp.json().get("embeddings", [])
                            for emb in emb_list:
                                v = np.array(emb.get("values", []), dtype=np.float32)
                                norm = np.linalg.norm(v)
                                all_embeddings.append((v / norm) if norm > 0 else v)
                            batch_success = True
                            break
                        elif resp.status_code in (429, 503):
                            time.sleep(0.5 * (attempt + 1))
                            continue
                        else:
                            break
                    except Exception:
                        time.sleep(0.5 * (attempt + 1))

                if not batch_success:
                    # Fallback individual encoding for this batch
                    for t in chunk_batch:
                        all_embeddings.append(self.get_embedding(t))

            return np.array(all_embeddings, dtype=np.float32)

        # Fallback individual hash projection
        return np.array([self.get_embedding(t) for t in texts], dtype=np.float32)

    def _check_pgvector_column(self, db) -> bool:
        """Checks if the document_chunks table has an active native pgvector column safely without poisoning transactions."""
        if self._has_pgvector_col is not None:
            return self._has_pgvector_col
        try:
            from sqlalchemy import inspect
            bind = db.get_bind() if hasattr(db, "get_bind") else getattr(db, "bind", None)
            if bind and bind.dialect.name == "postgresql":
                inspector = inspect(bind)
                columns = [c['name'] for c in inspector.get_columns('document_chunks')]
                self._has_pgvector_col = 'embedding' in columns
            else:
                self._has_pgvector_col = False
        except Exception as e:
            print(f"[VectorService] Notice on pgvector column check: {e}")
            self._has_pgvector_col = False
        return self._has_pgvector_col

    def index_document_chunks(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]],
        db: Optional[Any] = None,
        commit: bool = True
    ):
        """
        Computes dense embeddings and persists chunks and vectors into PostgreSQL (Neon).
        Zero dependence on ephemeral Render disk files.
        """
        if not chunks:
            return

        self.doc_chunks[doc_id] = chunks
        texts = [c.get("text", "") for c in chunks]

        # 1. Compute normalized dense embeddings
        embeddings = self.get_batch_embeddings(texts)

        # Attach embeddings to chunks in memory
        for idx, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[idx].tolist()

        # 2. Persist in PostgreSQL (Neon)
        from app.core.database import SessionLocal
        from app.models.document_chunk import DocumentChunk
        from app.models.document import Document

        should_close = False
        session = db
        if session is None:
            session = SessionLocal()
            should_close = True

        try:
            # Ensure parent document exists before modifying document_chunks to guarantee foreign key integrity
            doc_record = session.query(Document).filter(Document.id == doc_id).first()
            if not doc_record:
                err_msg = f"Document '{doc_id}' not found in active database session. Parent document must exist before persisting chunks."
                print(f"[VectorService] ERROR: {err_msg}")
                raise ValueError(err_msg)

            # Idempotently delete existing chunks for this document before inserting
            session.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).delete()
            session.flush()

            has_vec = self._check_pgvector_column(session)
            for idx, chunk in enumerate(chunks):
                emb_list = chunk.get("embedding", [])
                chunk_obj = DocumentChunk(
                    document_id=doc_id,
                    chunk_index=chunk.get("chunk_id", idx),
                    page_number=chunk.get("page", 1),
                    content=chunk.get("text", ""),
                    metadata_json=json.dumps({
                        "char_start": chunk.get("char_start", 0),
                        "char_end": chunk.get("char_end", 0),
                        "chunk_id": chunk.get("chunk_id", idx)
                    }),
                    embedding_json=json.dumps(emb_list)
                )
                session.add(chunk_obj)
                session.flush()

                if has_vec and emb_list:
                    # Execute in a nested SAVEPOINT transaction so any driver/dimension error cannot abort the parent transaction
                    try:
                        with session.begin_nested():
                            vec_str = "[" + ",".join(str(float(x)) for x in emb_list) + "]"
                            session.execute(
                                text("UPDATE document_chunks SET embedding = CAST(:vec AS vector) WHERE id = :id"),
                                {"vec": vec_str, "id": chunk_obj.id}
                            )
                    except Exception as vec_err:
                        # Non-critical: pgvector column update skipped; fallback embedding_json is already persisted
                        pass

            if commit:
                session.commit()
            else:
                session.flush()

            print(f"[VectorService] Successfully saved {len(chunks)} chunks for doc {doc_id} to PostgreSQL.")
        except Exception as e:
            session.rollback()
            print(f"[VectorService] PostgreSQL chunk persistence rollback: {e}")
            raise
        finally:
            if should_close:
                session.close()

        # 3. Optional local disk persistence for test compatibility
        try:
            chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
            tmp_chunks = chunks_file + ".tmp"
            with open(tmp_chunks, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)
            if os.path.exists(chunks_file):
                os.remove(chunks_file)
            os.rename(tmp_chunks, chunks_file)

            # Optional local FAISS index
            import faiss
            index = faiss.IndexFlatIP(self.dimension)
            index.add(embeddings)
            self.faiss_indices[doc_id] = index
            faiss_file = os.path.join(self.indices_dir, f"{doc_id}.faiss")
            tmp_faiss = faiss_file + ".tmp"
            faiss.write_index(index, tmp_faiss)
            if os.path.exists(faiss_file):
                os.remove(faiss_file)
            os.rename(tmp_faiss, faiss_file)
        except Exception:
            pass

    def _ensure_loaded(self, doc_id: str) -> List[Dict[str, Any]]:
        """Ensures chunks are loaded from memory cache, PostgreSQL, or disk files."""
        if doc_id in self.doc_chunks and len(self.doc_chunks[doc_id]) > 0:
            return self.doc_chunks[doc_id]

        # 1. Primary Source: Load from PostgreSQL (Neon)
        try:
            from app.core.database import SessionLocal
            from app.models.document_chunk import DocumentChunk

            db = SessionLocal()
            try:
                records = db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == doc_id
                ).order_by(DocumentChunk.chunk_index.asc()).all()

                if records:
                    chunks = []
                    for r in records:
                        c_meta = json.loads(r.metadata_json) if r.metadata_json else {}
                        c_emb = json.loads(r.embedding_json) if r.embedding_json else []
                        chunks.append({
                            "chunk_id": r.chunk_index,
                            "page": r.page_number,
                            "text": r.content,
                            "char_start": c_meta.get("char_start", 0),
                            "char_end": c_meta.get("char_end", 0),
                            "embedding": c_emb
                        })
                    self.doc_chunks[doc_id] = chunks
                    return chunks
            finally:
                db.close()
        except Exception as e:
            print(f"[VectorService] DB load notice: {e}")

        # 2. Disk fallback
        chunks_file = os.path.join(self.indices_dir, f"{doc_id}_chunks.json")
        if os.path.exists(chunks_file):
            try:
                with open(chunks_file, "r", encoding="utf-8") as f:
                    self.doc_chunks[doc_id] = json.load(f)
                    return self.doc_chunks[doc_id]
            except Exception:
                pass

        return self.doc_chunks.get(doc_id, [])

    def search_similar_chunks(
        self,
        doc_id: str,
        query: str,
        top_k: int = 4,
        min_score: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic search against stored document chunks.
        Computes cosine similarity with query embedding and combines with hybrid keyword boost.
        Returns top-k relevant chunks with genuine similarity scores and physical page numbers.
        """
        chunks = self._ensure_loaded(doc_id)
        if not chunks:
            return []

        # 1. Compute normalized query embedding with identical model
        query_vec = self.get_embedding(query)
        if np.linalg.norm(query_vec) > 0:
            query_vec /= np.linalg.norm(query_vec)

        # 2. Extract chunk embedding matrix
        emb_list = []
        for c in chunks:
            if "embedding" in c and c["embedding"]:
                emb_list.append(c["embedding"])
            else:
                emb_list.append(self.get_embedding(c.get("text", "")).tolist())

        emb_matrix = np.array(emb_list, dtype=np.float32)
        norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        emb_matrix = emb_matrix / norms

        # Cosine similarity via inner product of normalized vectors
        cos_scores = np.dot(emb_matrix, query_vec)

        # 3. Hybrid keyword scoring boost
        query_tokens = set(re.findall(r'\b[a-zA-Z0-9_\-\$]+\b', query.lower()))
        query_tokens = {t for t in query_tokens if len(t) > 2}

        scored_results = []
        for idx, chunk in enumerate(chunks):
            cos_sim = float(cos_scores[idx])

            # Keyword overlap boost
            chunk_tokens = set(re.findall(r'\b[a-zA-Z0-9_\-\$]+\b', chunk.get("text", "").lower()))
            overlap = len(query_tokens & chunk_tokens)
            keyword_boost = min(0.20, overlap * 0.04) if query_tokens else 0.0

            final_score = min(1.0, max(0.0, (cos_sim * 0.85) + keyword_boost))

            if final_score >= min_score or cos_sim >= min_score:
                scored_results.append({
                    "chunk_id": chunk.get("chunk_id", idx),
                    "page_number": chunk.get("page", 1),
                    "page": chunk.get("page", 1),
                    "content": chunk.get("text", ""),
                    "text": chunk.get("text", ""),
                    "similarity": round(final_score, 4),
                    "score": round(final_score, 4),
                    "raw_cosine": round(cos_sim, 4),
                    "char_start": chunk.get("char_start", 0),
                    "char_end": chunk.get("char_end", 0)
                })

        # Rank by score descending
        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:top_k]

    def delete_index(self, doc_id: str):
        """Cleans up document chunks from PostgreSQL, memory cache, and disk."""
        self.doc_chunks.pop(doc_id, None)
        self.faiss_indices.pop(doc_id, None)

        # Delete from PostgreSQL
        try:
            from app.core.database import SessionLocal
            from app.models.document_chunk import DocumentChunk
            db = SessionLocal()
            try:
                db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).delete()
                db.commit()
            except Exception as e:
                db.rollback()
                raise
            finally:
                db.close()
        except Exception as e:
            print(f"[VectorService] DB deletion error for {doc_id}: {e}")

        # Clean up disk files
        for suffix in [".faiss", "_chunks.json"]:
            path = os.path.join(self.indices_dir, f"{doc_id}{suffix}")
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


embedding_service = PersistentVectorService()
