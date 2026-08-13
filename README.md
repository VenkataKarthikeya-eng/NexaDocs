# NexaDocs — AI-Powered Document Intelligence Platform

> **Startup-Quality Enterprise Document Intelligence & RAG Workspace** built with React, Vite, Tailwind CSS, FastAPI, PostgreSQL, and FAISS Vector Search.

![NexaDocs Platform](https://img.shields.io/badge/NexaDocs-v2.4.0-blue.svg)
![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)
![License](https://img.shields.io/badge/License-MIT-slate.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![React](https://img.shields.io/badge/React-18.0-cyan.svg)

- **Live Demo**: [https://nexadocs.vercel.app](https://nexadocs.vercel.app)
- **GitHub Repository**: [https://github.com/VenkataKarthikeya-eng/NexaDocs](https://github.com/VenkataKarthikeya-eng/NexaDocs)

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

## 🧰 Technology Stack

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

## 📁 Project Structure

```
NexaDocs/
├── frontend/                 # React + Vite + Tailwind CSS + Framer Motion + Zustand
│   ├── src/
│   │   ├── components/       # Sidebar, Header, DocumentCard, UploadModal, ToastContainer
│   │   ├── pages/            # LandingPage, AuthPages, Dashboard, DocumentLibrary, AIWorkspace, Profile
│   │   ├── store/            # useAuthStore, useDocStore, useChatStore, useToastStore
│   │   ├── services/         # Axios client with JWT interceptor
│   │   └── App.jsx           # React Router v6
│   └── package.json
├── backend/                  # FastAPI + SQLAlchemy + JWT + FAISS RAG Engine
│   ├── app/
│   │   ├── api/              # auth, users, documents, ai endpoints
│   │   ├── core/             # config, security (JWT/bcrypt), database
│   │   ├── models/           # SQLAlchemy models (User, Document, ChatHistory, Insight)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   └── services/         # pdf_service, embedding_service, rag_service, storage_service
│   ├── uploads/              # Local PDF storage directory
│   ├── requirements.txt
│   └── render.yaml
├── docker-compose.yml        # PostgreSQL + FastAPI + React Vite orchestrator
├── .env.example              # Environment variables template
└── README.md
```

---

## 🚀 Local Installation & Setup

### 1. Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate | On macOS/Linux: source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run automated backend test suite
python test_backend.py

# Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger Docs: `http://localhost:8000/docs`

### 2. Frontend Setup (React + Vite)

```bash
cd frontend

# Install Node dependencies
npm install

# Test production build
npm run build

# Start Vite development server
npm run dev -- --port 5173
```
NexaDocs Web App: `http://localhost:5173`

---

## 🔑 Environment Setup

Create a `.env` file from `.env.example`:

```env
# Database Configuration
DATABASE_URL=postgresql://nexadocs_user:securepassword@localhost:5432/nexadocs_db

# JWT Security (Generate with: openssl rand -hex 32)
JWT_SECRET=<generate-secure-random-64-character-secret>

# AI LLM Provider Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Cloud File Storage (LOCAL, S3, CLOUDINARY)
STORAGE_PROVIDER=LOCAL
```

---

## 🔌 API Documentation

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

## ☁️ Deployment Guide

### Backend Deployment (Render)
1. Push codebase to GitHub repository: `https://github.com/VenkataKarthikeya-eng/NexaDocs`.
2. Connect repository in [Render Dashboard](https://dashboard.render.com/). Render will detect `backend/render.yaml` and deploy both the **Free Web Service** and **Free PostgreSQL Database**.

### Frontend Deployment (Vercel)
1. Import `frontend/` directory into Vercel.
2. Set Environment Variable `VITE_API_URL` to your Render API URL.
3. Vercel will build and host using `frontend/vercel.json` SPA rewrite rules.

---

## 📸 Screenshots

1. **Landing Page**: Enterprise hero section, trust indicators, and live product sandbox widget.
2. **Dashboard**: Storage meter, metrics cards, Recharts weekly document activity bar chart, and AI vector token trend area graph.
3. **3-Panel AI Workspace**: Document selector tree, center SSE streaming chat with exact source page citation badges (`📄 Page 4 [94% Match]`), and right automated insights panel.
4. **Document Library**: Grid/List view switcher, category tabs, and PDF dropzone modal.

---

## 👤 Developer

**CHERUKURI VENKATA KARTHIKEYA**
- **Email**: [venkatakarthikeya2005@gmail.com](mailto:venkatakarthikeya2005@gmail.com)
- **GitHub**: [https://github.com/VenkataKarthikeya-eng](https://github.com/VenkataKarthikeya-eng)
- **LinkedIn**: [https://www.linkedin.com/in/cherukuri-venkata-karthikeya-4b54393ab/](https://www.linkedin.com/in/cherukuri-venkata-karthikeya-4b54393ab/)

---

## 🛡️ License

Distributed under the MIT License. Copyright © 2026 NexaDocs Inc.
