# NexaDocs — Technical Project Summary

## 📌 Problem Statement
Enterprise teams, financial analysts, legal auditors, and researchers routinely handle hundreds of multi-page PDF documents. Navigating dense reports to extract key metrics, verify compliance SLAs, or locate specific data points is time-consuming, prone to human error, and lacks auditability.

## 💡 The Solution
**NexaDocs** is an AI-powered Document Intelligence Platform built on a multi-layered RAG (Retrieval-Augmented Generation) architecture. It enables users to upload PDF documents, automatically generates executive summaries and topic clusters, and allows instant natural language Q&A backed by exact page-level source citations.

---

## 🛠️ Key Technical Highlights

1. **Enterprise Light Theme SaaS UI**:
   - Built with React 18, Vite, and Tailwind CSS.
   - White canvas (`#FFFFFF`), light slate surfaces (`#F8FAFC`), crisp dark text (`#0F172A`), Google Font `Inter`, and professional blue (`#2563EB`) accents.
   - Styled after Linear, Stripe, and Vercel.

2. **FastAPI Async Backend & Security**:
   - Python ASGI framework with `bcrypt` password hashing and JWT bearer token authentication.
   - Strict file validation: 25MB max size limit and PDF file type enforcement.

3. **Multi-Tenant Database Architecture**:
   - PostgreSQL (Production on Render) with automatic SQLite fallback for local development via SQLAlchemy ORM.

4. **PDF Extraction & FAISS Vector Search Engine**:
   - PyPDF text extraction per page.
   - 500-character recursive chunking with 100-character overlaps.
   - FAISS vector store indexing (`IndexFlatIP`) with fallback NumPy cosine similarity search.

5. **Server-Sent Events (SSE) AI Response Streaming**:
   - Real-time progressive token streaming via `/api/v1/ai/chat/stream` with a functional Stop Generation button.

6. **Page-Level Source Citations & Match Scoring**:
   - Returns metadata: `page_number`, `section_name`, `chunk_id`, `relevance_score` (`94% Match`).

7. **Production Cloud Deployment Configurations**:
   - Frontend: Vercel CDN deployment (`vercel.json` SPA rewrite rules).
   - Backend: Render hosting (`render.yaml` with Uvicorn ASGI server).
   - Containerization: `docker-compose.yml` orchestrating PostgreSQL, FastAPI backend, and React Vite frontend.

---

## 🔑 Demo Credentials

- **Email**: `demo@nexadocs.com`
- **Password**: `Demo@123`
- **Preloaded Documents**:
  1. *Enterprise Financial Report.pdf*
  2. *AI Research Paper.pdf*
  3. *Technical Architecture Document.pdf*
