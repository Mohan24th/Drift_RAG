
# Drift RAG

Drift RAG is a version-aware Retrieval-Augmented Generation (RAG) platform
for managing and querying company knowledge bases.

It allows employees to ask questions against approved company documents,
while HR/Admin users can manage documents, upload new versions, approve
versions, and analyze knowledge drift between document versions.

## Live Demo

**Frontend:**  
https://drift-rag.vercel.app

**Backend:**  
https://drift-rag.onrender.com

**API Documentation:**  
https://drift-rag.onrender.com/docs

---

# What Problem Does Drift RAG Solve?

Traditional RAG systems can continue answering questions after a
document changes without clearly showing whether the underlying knowledge
used for retrieval has changed.

Drift RAG introduces document versioning and drift analysis so that
organizations can understand how changes in their knowledge base affect
retrieval results.

For example:

```text
Leave Policy v4
      ↓
Leave Policy v5
      ↓
Compare retrieval behavior
      ↓
Identify affected questions
````

The system measures:

* Retrieval overlap
* Retrieval ranking changes
* Semantic/content changes

---

# Key Features

## Authentication and Authorization

The system uses JWT-based authentication with role-based access control.

Supported roles:

```text
EMPLOYEE
HR
ADMIN
```

Permissions are separated by role.

### Employee

Employees can:

* Log in
* View approved company documents
* Ask questions about approved documents
* View generated answers
* View the retrieved sources

### HR / Admin

HR and Admin users can:

* Create documents
* Upload document versions
* View version history
* Approve versions
* Analyze drift between versions
* Manage the company knowledge base

---

# Document Versioning

Documents are treated as versioned entities.

Example:

```text
Leave Policy

v1
v2
v3
v4
v5
```

A newly uploaded version starts as:

```text
DRAFT
```

After approval:

```text
APPROVED
```

When a newer version is approved, the previous approved version is
archived:

```text
v4 APPROVED

      ↓ approve v5

v4 ARCHIVED
v5 APPROVED
```

Employees only interact with documents that have an approved version.

---

# RAG Pipeline

The document ingestion pipeline is:

```text
Document
   ↓
Upload
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embedding Generation
   ↓
PostgreSQL + pgvector
   ↓
Similarity Retrieval
   ↓
Context Construction
   ↓
LLM
   ↓
Answer + Sources
```

The embedding model currently uses:

```text
all-MiniLM-L6-v2
```

The generated answer is produced using the configured Groq LLM.

---

# Drift Analysis

Drift RAG compares two document versions for the same document.

Example:

```text
v4
 ↓
v5
```

For a set of questions, the system evaluates:

### Retrieval Overlap

Measures how much the retrieved chunks overlap between versions.

### Ranking Drift

Measures changes in the ordering/ranking of retrieved chunks.

### Semantic Drift

Measures how significantly the retrieved content changes between
versions.

The result identifies questions whose answers may be affected by changes
in the knowledge base.

---

# System Architecture

```text
                         ┌───────────────────────┐
                         │       Employee        │
                         │       Browser         │
                         └───────────┬───────────┘
                                     │
                                     │ HTTPS
                                     ▼
                         ┌───────────────────────┐
                         │      Vercel           │
                         │   React + Vite        │
                         └───────────┬───────────┘
                                     │
                                     │ REST API
                                     ▼
                         ┌───────────────────────┐
                         │      Render           │
                         │      FastAPI           │
                         └───────────┬───────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
                 ▼                   ▼                   ▼
        ┌────────────────┐   ┌────────────────┐   ┌───────────────┐
        │ PostgreSQL     │   │ Supabase       │   │ Groq          │
        │ + pgvector     │   │ Storage        │   │ LLM           │
        └────────────────┘   └────────────────┘   └───────────────┘
```

---

# Tech Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* pgvector
* Sentence Transformers
* Pydantic
* Uvicorn

## AI / RAG

* Sentence Transformers
* `all-MiniLM-L6-v2`
* Groq
* Vector similarity retrieval
* Version-aware retrieval
* Drift analysis

## Storage

* Supabase Storage
* Local storage support for development

## Authentication

* JWT
* `python-jose`
* bcrypt
* Role-based authorization

## Frontend

* React
* Vite
* React Router
* Nginx

## DevOps

* Docker
* Docker Compose
* Render
* Vercel
* GitHub

## Testing

* pytest
* FastAPI TestClient
* API tests
* ingestion tests
* retrieval tests
* drift tests

---

# Project Structure

```text
drift-rag/
│
├── app/
│   ├── api/
│   │   ├── main.py
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── documents.py
│   │       ├── drift.py
│   │       └── query.py
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── security.py
│   │   └── service.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── document_service.py
│   │   ├── models.py
│   │   └── repositories/
│   │       └── documents.py
│   │
│   ├── drift/
│   │   ├── analyzer.py
│   │   ├── metrics.py
│   │   ├── report.py
│   │   ├── retrieval.py
│   │   ├── semantic.py
│   │   ├── service.py
│   │   ├── summary.py
│   │   └── version_loader.py
│   │
│   ├── generation/
│   │   ├── llm.py
│   │   ├── models.py
│   │   ├── qa.py
│   │   └── service.py
│   │
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── loader.py
│   │   ├── pdf_loader.py
│   │   └── service.py
│   │
│   ├── retrieval/
│   │   ├── embeddings.py
│   │   └── pg_retriever.py
│   │
│   ├── storage/
│   │   ├── base.py
│   │   ├── dependencies.py
│   │   ├── local.py
│   │   └── supabase.py
│   │
│   └── config.py
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── auth/
│   │   │   ├── AuthContext.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── pages/
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── EmployeeApp.jsx
│   │   │   └── Login.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── tests/
│   ├── test_api_admin_documents.py
│   ├── test_api_documents.py
│   ├── test_api_drift.py
│   ├── test_api_errors.py
│   ├── test_api_health.py
│   ├── test_api_query.py
│   └── test_ingestion.py
│
├── scripts/
│   ├── create_tables.py
│   ├── create_user.py
│   ├── evaluate_pg_retrieval.py
│   ├── evaluate_rag.py
│   ├── inspect_database.py
│   ├── list_versions.py
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

---

# Local Development

## 1. Clone the repository

```bash
git clone https://github.com/Mohan24th/Drift_RAG.git
cd Drift_RAG
```

## 2. Create a Python environment

```bash
python -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create:

```text
.env
```

Example structure:

```env
DATABASE_URL=...

GROQ_API_KEY=...

JWT_SECRET_KEY=...

EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=openai/gpt-oss-20b

API_HOST=127.0.0.1
API_PORT=8000

DOCUMENT_STORAGE=supabase
DOCUMENT_STORAGE_PATH=data/documents

SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
SUPABASE_STORAGE_BUCKET=drift-rag-documents

CORS_ORIGINS=http://localhost:5173
```

Never commit `.env` or other secrets to Git.

---

# Run the Backend

```bash
uvicorn app.api.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

Readiness check:

```text
http://127.0.0.1:8000/ready
```

---

# Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

Configure the backend URL with:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

# Docker

The backend and frontend can be run together using Docker Compose.

Build and start:

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d --build
```

Check running services:

```bash
docker compose ps
```

Stop services:

```bash
docker compose down
```

Local URLs:

```text
Frontend:
http://localhost:5173

Backend:
http://localhost:8000

API Docs:
http://localhost:8000/docs
```

---

# API Overview

## Authentication

```text
POST /auth/login
```

## Documents

```text
GET  /documents/
POST /documents/

GET  /documents/available

GET  /documents/{document_id}

GET  /documents/{document_id}/versions

POST /documents/{document_id}/versions

POST /documents/{document_id}/versions/{version_number}/approve
```

## Query

```text
POST /documents/{document_id}/query
```

## Drift

```text
POST /documents/{document_id}/drift
```

## Health

```text
GET /health
GET /ready
```

Full interactive documentation is available through Swagger:

```text
/docs
```

---

# Document Lifecycle

A typical document workflow looks like:

```text
Create Document
      ↓
Upload v1
      ↓
DRAFT
      ↓
Approve
      ↓
APPROVED
      ↓
Employees can query
```

When a new version is uploaded:

```text
v1 APPROVED
     ↓
Upload v2
     ↓
v2 DRAFT
```

After approval:

```text
v1 ARCHIVED
v2 APPROVED
```

This ensures the employee-facing application works against the current
approved knowledge.

---

# Employee Workflow

```text
Employee Login
      ↓
Approved Documents
      ↓
Select Document
      ↓
Ask Question
      ↓
Vector Retrieval
      ↓
Relevant Context
      ↓
LLM Generation
      ↓
Answer
      ↓
Sources
```

The employee UI intentionally exposes approved knowledge rather than
draft versions or internal storage details.

---

# HR / Admin Workflow

```text
HR / Admin Login
      ↓
Document Dashboard
      ↓
Create Document
      ↓
Upload Version
      ↓
Review Version
      ↓
Approve
      ↓
Previous Version Archived
      ↓
Run Drift Analysis
```

---

# Testing

Run the complete backend test suite:

```bash
python -m pytest -q
```

Run frontend production build:

```bash
cd frontend
npm run build
```

Run Docker:

```bash
docker compose up --build
```

Then verify:

```text
GET /health
GET /ready
Login
Employee query
HR document management
Version approval
Drift analysis
```

---

# Deployment

## Backend

The backend is containerized using Docker and deployed on Render.

Production backend:

```text
https://drift-rag.onrender.com
```

## Frontend

The React frontend is deployed on Vercel.

Production frontend:

```text
https://drift-rag.vercel.app
```

## Production Flow

```text
GitHub
   │
   ├── Vercel
   │     └── React Frontend
   │
   └── Render
         └── FastAPI Backend
                │
                ├── Supabase PostgreSQL
                ├── Supabase Storage
                └── Groq
```

---

# Security Notes

* Secrets are stored through environment variables.
* JWT authentication protects API access.
* Role-based access control protects HR/Admin operations.
* Employees cannot upload or approve documents.
* Draft document versions are not exposed through the employee document
  endpoint.
* Supabase Storage is used for persistent document storage.

---

# Current Status

The project currently includes:

```text
 FastAPI backend
 PostgreSQL + pgvector
 RAG retrieval
 LLM generation
 Document versioning
 Approval workflow
 Archived version handling
 JWT authentication
 RBAC
 Supabase Storage
 React frontend
 Employee interface
 HR/Admin dashboard
 Drift analysis
 Automated tests
 Docker
 Docker Compose
 Render deployment
 Vercel deployment
```

---

# Future Improvements

Potential next steps include:

* AI-generated explanations of detected drift
* More comprehensive end-to-end browser tests
* CI/CD with automated test gates
* Observability and structured logging
* Improved retrieval evaluation
* Better document preview and management
* Production monitoring
* Rate limiting and additional API hardening

