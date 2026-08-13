# NexaDocs — AI-Powered Document Intelligence Platform

> **Startup-Quality Enterprise Document Intelligence & RAG Workspace** built with React, Vite, Tailwind CSS, FastAPI, PostgreSQL, and FAISS Vector Search.

![NexaDocs Platform](https://img.shields.io/badge/NexaDocs-v2.4.0-blue.svg)
![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)
![License](https://img.shields.io/badge/License-MIT-slate.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![React](https://img.shields.io/badge/React-18.0-cyan.svg)

---

## 🌟 Product Overview

**NexaDocs** helps enterprise teams upload complex documents (financial audits, technical architecture blueprints, security SLAs, research papers), manage knowledge bases, and interact with structured knowledge through an intelligent 3-panel RAG workspace.

Built with modern SaaS principles:
- **Clean White Interface (`#FFFFFF`) & Neutral Slate Surfaces (`#F8FAFC`)**: Styled after Stripe, Linear, and Vercel.
- **Strictly No Gimmicks**: Non-robotic, enterprise light theme without dark mode defaults or neon effects.
- **Page-Level Source Citations**: Every AI response includes exact page citations, section headers, and relevance match scores (`94% Match`).

---

## 🏗️ Technical Architecture

```
User (Browser SPA)
       │
       ├──► React 18 + Vite + Tailwind CSS (Vercel CDN)
       │          │ (Axios REST + SSE Streaming)
       │          ▼
       └──► FastAPI Async Backend (Render Web Service)
                  │
                  ├──► JWT Authentication & bcrypt Password Hashing
                  │
                  ├──► PyPDF / PDFPlumber Text Extractor
                  │
                  ├──► Recursive 500-char Chunking & FAISS Vector Indexing
                  │
                  ├──► RAG Context Retrieval & OpenAI LLM Engine
                  │
                  └──► PostgreSQL / SQLite Database (Render Postgres)
```

---

## 🧰 Tech Stack

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS + Google Fonts Inter
- **State Management**: Zustand (`useAuthStore`, `useDocStore`, `useChatStore`, `useToastStore`)
- **Analytics**: Recharts (Weekly Activity Bar & AI Token Area Charts)
- **HTTP Client**: Axios with automatic JWT bearer interceptors

### Backend
- **Framework**: FastAPI + Uvicorn (ASGI)
- **Database**: PostgreSQL (Production) / SQLite (Local Dev) via SQLAlchemy ORM
- **Security**: JWT (`python-jose`) + `bcrypt` password hashing
- **PDF Extraction**: PyPDF / PDFPlumber
- **Vector Search**: FAISS (`faiss-cpu`) + Cosine Vector Engine
- **RAG Engine**: LangChain / SentenceTransformers / OpenAI API with fallback intelligence generator

---

## 🚀 Quickstart Guide (Local Development)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run automated test suite
python test_backend.py

# Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger Documentation: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Test production build
npm run build

# Launch Vite development server
npm run dev -- --port 5173
```
NexaDocs SaaS Application: `http://localhost:5173`

---

## 🐳 Docker Deployment

```bash
# Spin up PostgreSQL, FastAPI Backend, and Vite Frontend
docker-compose up --build
```

---

## 🔑 Environment Configuration

Create a `.env` file from `.env.example`:

```env
# Database Configuration
DATABASE_URL=postgresql://nexadocs_user:securepassword@localhost:5432/nexadocs_db

# JWT Security (Generate with: openssl rand -hex 32)
JWT_SECRET=<generate-secure-random-64-character-secret>

# Cloud File Storage (LOCAL, S3, CLOUDINARY)
STORAGE_TYPE=LOCAL
AWS_S3_BUCKET=nexadocs-production-bucket
AWS_REGION=us-east-1

# AI LLM Provider Key
OPENAI_API_KEY=sk-your-openai-api-key-here
```

---

## 🔌 API Endpoint Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register account & return JWT |
| `POST` | `/api/v1/auth/login` | Authenticate & return JWT |
| `GET` | `/api/v1/auth/me` | Return authenticated user details |
| `POST` | `/api/v1/documents/upload` | Upload PDF file & trigger FAISS indexing |
| `GET` | `/api/v1/documents` | List user documents |
| `DELETE` | `/api/v1/documents/{id}` | Delete document & vector index |
| `POST` | `/api/v1/ai/chat` | RAG context search & answer with page citations |
| `POST` | `/api/v1/ai/chat/stream` | Server-Sent Events (SSE) progressive token stream |
| `GET` | `/api/v1/ai/insights/{doc_id}` | Fetch summary, topics, and entity extractions |

---

## 🔑 Preloaded Demo Credentials

For instant demonstration access without registering:
- **Email**: `sarah.j@enterprise.com`
- **Password**: `••••••••••••`
- **Preloaded Documents**: *Q3 Enterprise Financial Report.pdf*, *NexaDocs Technical Blueprint.pdf*, *SOC2 Security SLA.pdf*.

---

## 📸 Portfolio Screenshots Checklist

1. `landing_page.png` — Hero section, trust badges, and interactive workspace sandbox tabs.
2. `dashboard.png` — Analytics cards, storage meter, and Recharts activity graphs.
3. `ai_workspace.png` — 3-panel RAG workspace showing document list, SSE streamed chat with page citations (`📄 Page 4 [94% Match]`), and right insights panel.
4. `document_library.png` — Search filter, category tabs, and drag & drop upload dropzone.

---

## 📝 Resume & Portfolio Description

**NexaDocs — Full-Stack AI Document Intelligence Platform**
- Architected an enterprise-grade document intelligence platform processing multi-page PDFs using FastAPI, React 18, and FAISS vector indexing.
- Implemented RAG (Retrieval-Augment Generation) context search with recursive chunking and exact page-level source citations.
- Engineered a 3-Panel workspace featuring Server-Sent Events (SSE) token streaming, automated executive summaries, and entity extractions.
- Built production deployment pipeline with Docker Compose, Render PostgreSQL, Vercel SPA routing, and JWT authentication with bcrypt password hashing.

---

## 🛡️ License

Distributed under the MIT License. Copyright © 2026 NexaDocs Inc.
