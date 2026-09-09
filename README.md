# NexaDocs — AI-Powered Document Intelligence Platform

> **Enterprise Document Intelligence & RAG Workspace** built with React 19, Vite, Tailwind CSS, FastAPI, PostgreSQL, and FAISS Vector Search.

![NexaDocs Platform](https://img.shields.io/badge/NexaDocs-v2.4.0-blue.svg)
![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)
![License](https://img.shields.io/badge/License-MIT-slate.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![React](https://img.shields.io/badge/React-19.0-cyan.svg)

- **Live Frontend**: [https://nexa-docs.vercel.app/](https://nexa-docs.vercel.app/)
- **Backend Deployment**: Planned on Render (FastAPI ASGI Web Service + Render PostgreSQL)
- **GitHub Repository**: [https://github.com/VenkataKarthikeya-eng/NexaDocs](https://github.com/VenkataKarthikeya-eng/NexaDocs)

---

## 🌟 Product Overview

**NexaDocs** is an AI-powered Document Intelligence Platform designed for enterprise teams, financial analysts, legal auditors, and researchers. It allows users to upload multi-page PDF documents, automatically extracts and chunks textual layers, indexes embeddings into a persistent FAISS vector store, and provides natural-language Q&A powered by a multi-layered RAG (Retrieval-Augmented Generation) pipeline with page-level citations and real-time Server-Sent Events (SSE) token streaming.

---

## ✨ Key Features

1. **PDF Document Intelligence**:
   - Multi-page text extraction with PyPDF.
   - Enforces 25MB file size limit and strict PDF file type validation.
   - Recursive 500-character chunking with 100-character overlap preserving page and chunk metadata.

2. **RAG Chatbot with Page-Level Citations**:
   - Natural language question-answering over uploaded documents.
   - Every answer includes verified page citations, section references, and relevance confidence scores (e.g., `94% Match`).

3. **Persistent FAISS Vector Search**:
   - C++ accelerated vector similarity search using `faiss-cpu` (`IndexFlatIP`).
   - Persistent index storage on disk (`.faiss` and `_chunks.json`) ensuring knowledge bases survive server restarts.
   - On-demand index reconstruction fallback from original documents.

4. **Automated AI Insights**:
   - Automatic generation of executive summaries, topic clusters, entity extractions, and key takeaways for each document.
   - Cross-document topic and entity aggregation.

5. **Enterprise JWT Authentication**:
   - Secure token-based authentication with `bcrypt` password hashing.
   - Protected API routes, user profile management, and PostgreSQL session persistence.

6. **Real-Time SSE Streaming**:
   - Progressive token streaming via Server-Sent Events (`/api/v1/ai/chat/stream`).
   - Interactive stream cancellation with a dedicated stop-generation control.

---

## 🧰 Technology Stack

### Frontend
- **React 19**: Modern UI component architecture
- **Vite**: Ultra-fast build tool and development server
- **Tailwind CSS**: Professional enterprise light-theme styling (Inter font, slate surfaces, blue accents)
- **Zustand**: Reactive state management (`useAuthStore`, `useDocStore`, `useChatStore`, `useToastStore`)
- **Recharts**: Document activity analytics and token consumption trajectory
- **Lucide React**: Clean, accessible enterprise icons
- **Axios**: HTTP client with JWT interceptor

### Backend
- **FastAPI**: High-performance asynchronous Python ASGI framework
- **SQLAlchemy 2.0**: Object-relational mapping and database session management
- **PostgreSQL**: Production-grade relational database for users, documents, chat histories, and insights
- **Uvicorn**: Lightning-fast ASGI production server
- **Pydantic v2 & Pydantic-Settings**: Strict data validation and environment configuration
- **python-jose & bcrypt**: JWT bearer tokens and password hashing

### AI & Vector Engine
- **FAISS (`faiss-cpu`)**: High-speed vector similarity search and index persistence
- **RAG Architecture**: Contextual chunk retrieval and synthesis pipeline
- **Embeddings**: Normalized vector representations with SentenceTransformers / OpenAI integration

---

## 🏗️ System Architecture

```
                                  +---------------------------------------+
                                  |         User Web Browser (SPA)        |
                                  |    https://nexa-docs.vercel.app/      |
                                  +-------------------+-------------------+
                                                      |
                                                      | HTTPS (REST / SSE Stream)
                                                      v
                                  +---------------------------------------+
                                  |      FastAPI ASGI Backend Server      |
                                  |      (Deployment planned on Render)   |
                                  +---------+-------------------+---------+
                                            |                   |
                     +----------------------+                   +-----------------------+
                     |                                                                  |
                     v                                                                  v
+---------------------------------------+                              +---------------------------------------+
|        PostgreSQL Database            |                              |        FAISS Vector Storage           |
|---------------------------------------|                              |---------------------------------------|
| - users                               |                              | - uploads/indices/{doc_id}.faiss      |
| - documents                           |                              | - uploads/indices/{doc_id}_chunks.json|
| - chat_history                        |                              | - Inner Product (IP) Similarity       |
| - insights                            |                              | - Persistent across Server Restarts   |
+---------------------------------------+                              +---------------------------------------+
                     ^                                                                  ^
                     |                                                                  |
                     +----------------------+                   +-----------------------+
                                            |                   |
                                  +---------+-------------------+---------+
                                  |         RAG Intelligence Engine       |
                                  |---------------------------------------|
                                  | 1. PyPDF Text Layer Extraction        |
                                  | 2. Recursive Overlapping Chunking     |
                                  | 3. Normalized Vector Embedding        |
                                  | 4. Context Synthesis & Citations      |
                                  | 5. Token Streaming Generator (SSE)    |
                                  +---------------------------------------+
```

---

## 📁 Repository Structure

```
NexaDocs/
├── frontend/                 # React 19 + Vite + Tailwind CSS SPA
│   ├── src/
│   │   ├── components/       # Layout, Sidebar, Header, DocumentCard, UploadModal, ToastContainer
│   │   ├── pages/            # LandingPage, AuthPages, Dashboard, DocumentLibrary, AIWorkspace, InsightsPage, ReportsPage, ProfilePage
│   │   ├── store/            # useAuthStore, useDocStore, useChatStore, useToastStore
│   │   ├── services/         # Axios API client with JWT interceptor
│   │   └── App.jsx           # React Router DOM v7 route definitions
│   ├── vercel.json           # Vercel SPA rewrite configuration
│   ├── package.json
│   └── vite.config.js
├── backend/                  # FastAPI + SQLAlchemy + PostgreSQL + FAISS RAG Engine
│   ├── app/
│   │   ├── api/              # auth, users, documents, ai endpoints (mounted on /api/v1 and /api)
│   │   ├── core/             # config, security (JWT/bcrypt), database engine
│   │   ├── models/           # User, Document, ChatHistory, Insight SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # pdf_service, embedding_service, rag_service, storage_service
│   ├── uploads/              # Local storage for PDF files and FAISS indices (gitignored)
│   ├── test_backend.py       # 13-step automated backend test suite
│   ├── requirements.txt
│   └── render.yaml           # Render service specification
├── docker-compose.yml        # PostgreSQL 15 + FastAPI + React Vite container orchestration
├── render.yaml               # Root Render Blueprint specification (planned deployment)
├── .env.example              # Environment template
└── README.md
```

---

## 🔑 Environment Configuration

### Backend (`backend/.env`)

```env
# Database Connection (PostgreSQL)
DATABASE_URL=postgresql://nexadocs_user:securepassword@localhost:5432/nexadocs_db

# JWT Security
JWT_SECRET=your-secure-random-64-character-secret

# AI LLM Provider Key (Optional: enable for OpenAI GPT synthesis)
OPENAI_API_KEY=

# Storage Provider (LOCAL, S3, CLOUDINARY)
STORAGE_TYPE=LOCAL
ENVIRONMENT=development
```

### Frontend (`frontend/.env`)

```env
# Target Backend API URL
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🚀 Local Development Setup

### Prerequisites
- **Python**: 3.10, 3.11, or 3.12+
- **Node.js**: v18+ (tested on Node v20/v24) & npm
- **PostgreSQL**: Version 14+ (tested on PostgreSQL 18.4)

### 1. Database Setup
Ensure PostgreSQL is running and create the user and database:
```sql
CREATE USER nexadocs_user WITH PASSWORD 'securepassword';
CREATE DATABASE nexadocs_db OWNER nexadocs_user;
GRANT ALL ON SCHEMA public TO nexadocs_user;
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Run automated verification test suite
python test_backend.py

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
Interactive API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Frontend Setup

```bash
cd frontend

# Install packages
npm install

# Create .env
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Run production build check
npm run build

# Start Vite development server
npm run dev
```
Access the application at `http://localhost:5173`.

### 4. Running with Docker Compose

To launch the entire stack (PostgreSQL, FastAPI backend, and React frontend) using Docker:

```bash
docker-compose up --build
```

---

## 🔌 API Endpoints Summary

Both `/api/v1` and legacy `/api` routes are supported for full backward compatibility:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` or `/api/v1/health` | Service health status check |
| `POST` | `/api/v1/auth/register` | Register new user & issue JWT |
| `POST` | `/api/v1/auth/login` | Authenticate credentials & return JWT |
| `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile |
| `PUT` | `/api/v1/users/profile` | Update profile attributes (name, role, plan) |
| `POST` | `/api/v1/documents/upload` | Upload PDF, parse text, chunk, and index in FAISS |
| `GET` | `/api/v1/documents` | List user documents with summaries and topics |
| `GET` | `/api/v1/documents/{id}` | Get document metadata and insights |
| `DELETE` | `/api/v1/documents/{id}` | Delete document, PDF file, and FAISS vector index |
| `POST` | `/api/v1/ai/chat` | Query document using RAG retrieval with source citations |
| `POST` | `/api/v1/ai/chat/stream` | Server-Sent Events (SSE) progressive token stream |
| `GET` | `/api/v1/ai/chat/history/{doc_id}` | Retrieve stored conversation history for a document |
| `GET` | `/api/v1/ai/insights/{doc_id}` | Retrieve extracted topics, entities, and highlights |

---

## ☁️ Production Deployment Instructions

### Frontend (Live on Vercel)
- **Live URL**: [https://nexa-docs.vercel.app/](https://nexa-docs.vercel.app/)
- **Configuration**: `frontend/vercel.json` provides single-page application (SPA) routing rewrites.
- **Environment Variable**: Configure `VITE_API_URL` in Vercel project settings pointing to the deployed backend URL.

### Backend (Deployment Planned on Render)
> **Note**: Backend deployment on Render is planned and configured via `render.yaml`. It has not yet been executed in production.

To deploy on Render:
1. Push the repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), select **New > Blueprint**.
3. Connect the repository. Render will automatically parse `render.yaml` to provision:
   - **`nexadocs-api`**: Python web service (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
   - **`nexadocs-db`**: Managed PostgreSQL database instance.
4. Render will automatically link the database connection string via `DATABASE_URL` and generate a cryptographically secure `JWT_SECRET`.
5. Update `VITE_API_URL` in the Vercel project settings with the generated Render backend URL.

---

## 👤 Developer & Maintainer

**CHERUKURI VENKATA KARTHIKEYA**
- **Email**: [venkatakarthikeya2005@gmail.com](mailto:venkatakarthikeya2005@gmail.com)
- **GitHub**: [https://github.com/VenkataKarthikeya-eng](https://github.com/VenkataKarthikeya-eng)
- **LinkedIn**: [https://www.linkedin.com/in/cherukuri-venkata-karthikeya-4b54393ab/](https://www.linkedin.com/in/cherukuri-venkata-karthikeya-4b54393ab/)

---

## 🛡️ License

Distributed under the MIT License. Copyright © 2026 NexaDocs Inc.
