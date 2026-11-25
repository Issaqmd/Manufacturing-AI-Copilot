# Manufacturing AI Copilot

**Live Public Demo:** [https://manufacturing-ai-copilot-3087.onrender.com](https://manufacturing-ai-copilot-3087.onrender.com)  
*(Note: Hosted on Render's free tier; if inactive for 15+ minutes, the initial request takes ~30–50 seconds for container cold start, after which queries complete in ~5–7 seconds.)*

---

## 1. Overview & Problem Statement

On a manufacturing shop floor, supervisors, operators, and quality control (QC) inspectors frequently need immediate answers from equipment manuals, incoming inspection Standard Operating Procedures (SOPs), and Lockout/Tagout (LOTO) safety protocols. Searching multi-page PDFs manually slows down floor decisions, while standard AI chatbots risk fabricating specifications or retrieving outdated document revisions.

**Manufacturing AI Copilot** is a lightweight, document-grounded Retrieval-Augmented Generation (RAG) web application built for shop-floor teams at **Kaveri Precision Components Pvt. Ltd. (Hosur Plant)**. It delivers cited, role-aware operational answers with zero hallucination and built-in revision supersession detection.

---

## 2. Implemented Features

* **Document-Grounded RAG Pipeline:** Retrieves relevant passages from indexed plant PDFs using local FAISS vector similarity search and generates responses strictly bounded to the retrieved context.
* **Automated Document Revision & Supersession Guard:** During PDF ingestion (`app/pdf_processor.py`), a two-pass header parser extracts Document IDs, revision numbers, and effective dates. When an older revision (`QC-SOP-014 Rev 03`, 15-Mar-2023) is superseded by a newer one (`QC-SOP-014 Rev 04`, 01-Jul-2026), older chunks are flagged `SUPERSEDED` so the Copilot enforces the active procedure and warns against obsolete rules.
* **Role Authorization & Safety Callouts:** Explicitly identifies who is authorized to perform an action (Operator, Maintenance Technician, Shift Supervisor, Production Manager, Safety Officer, or SQE) and surfaces mandatory LOTO (`SAF-SOP-003`) precautions.
* **Strict Refusal Logic:** Refuses to guess or extrapolate when requested values (such as unmentioned bolt torque specs) do not exist in the plant documentation.
* **Industrial SaaS Web Interface (`static/index.html`):**
  * **One-Tap Quick Query Chips:** Enables fast execution of common shop-floor checks on desktop or mobile browsers.
  * **Expandable Source Verification Drawers:** Clicking any citation badge (`Doc ID (Revision) • Pg X`) reveals the verbatim extracted PDF text snippet for immediate verification.

---

## 3. Technology Stack & System Architecture

| Layer | Technology | Role in System |
| :--- | :--- | :--- |
| **Backend API** | FastAPI + Uvicorn | Serves REST endpoints (`/api/ask`, `/api/health`) and hosts the static frontend UI from a single process. |
| **PDF Ingestion** | PyMuPDF (`pymupdf`) | Extracts page-level text and parses Document ID, revision, and effective date metadata. |
| **Vector Search** | FAISS (`faiss-cpu`) + NumPy | Executes local L2 similarity search over precomputed embeddings with minimal RAM footprint. |
| **AI Models** | Google Gemini REST API | Uses `gemini-embedding-001` for 3072-dim text embeddings and `gemini-3.5-flash` for grounded response synthesis via lightweight `urllib.request` REST calls. |
| **Frontend UI** | HTML5, CSS3, Vanilla JS | Responsive industrial interface with zero heavy frontend build dependencies. |
| **Cloud Hosting** | Render (Blueprint / Free Web Service) | Configured via `render.yaml` with environment-managed secrets. |

### Data Flow
```text
User Question (Web UI)
       │
       ▼
POST /api/ask (FastAPI)
       │
       ├──► 1. Embed query via Gemini REST API (gemini-embedding-001)
       ├──► 2. Retrieve top-k matching chunks from local FAISS index (faiss.index)
       ├──► 3. Attach revision status (ACTIVE vs SUPERSEDED) & page metadata
       └──► 4. Generate grounded answer via Gemini REST API (gemini-3.5-flash)
       │
       ▼
JSON Response { answer, sources[], grounded } ──► Rendered with clickable source drawers
```

---

## 4. Project Structure

```text
BiztelAI-Copilot/
├── .env.example               # Template for required environment variables
├── .gitignore                 # Excludes .env secrets, virtual environments, and caches
├── render.yaml                # Render Blueprint deployment configuration
├── requirements.txt           # Lightweight Python dependencies
├── README.md                  # Project documentation and evaluation summary
├── THINKING.md                # Initial user journey, AI critique, and post-build reflection
├── ingest.py                  # Offline script to extract PDFs, detect revisions, and build FAISS index
├── run.py                     # Local Uvicorn server entry point
├── app/
│   ├── config.py              # Environment variable and path configuration
│   ├── pdf_processor.py       # PyMuPDF text extraction, chunking, and revision supersession detector
│   ├── rag_engine.py          # FAISS similarity search and Gemini REST API client
│   └── main.py                # FastAPI routes and static file serving
├── data/
│   ├── pdfs/                  # Source plant SOPs and maintenance manuals
│   └── index/                 # Prebuilt FAISS vector index and chunk metadata JSON
├── static/
│   └── index.html             # Industrial SaaS frontend UI
└── tests/
    └── evaluate_questions.py  # Automated evaluation script (5 sample + 5 custom queries)
```

---

## 5. Local Setup & Running Instructions

### 1. Clone & Create Virtual Environment
```powershell
git clone [https://github.com/Issaqmd/BiztelAI-Copilot.git](https://github.com/Issaqmd/BiztelAI-Copilot.git)
cd BiztelAI-Copilot

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your Google AI Studio API key:
```powershell
Copy-Item .env.example .env
```
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
EMBEDDING_MODEL=gemini-embedding-001
HOST=0.0.0.0
PORT=8000
```

### 3. Build Index (Optional — Prebuilt Index Included) & Start Server
```powershell
python ingest.py
python run.py
```
Open `http://localhost:8000` in your browser.

---

## 6. Deployment (Render)

Deployment is defined in `render.yaml`:
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* **Required Secret:** `GEMINI_API_KEY` set in the Render dashboard environment settings (never committed to Git).

---

## 7. Current Limitations & Future Improvements

### Honest Limitations
* **Cold-Start Latency:** On Render's free tier, inactive containers sleep after 15 minutes, causing a ~30–50 second wake-up delay on the first request.
* **Text-Based PDF Extraction:** Current chunking relies on `PyMuPDF` text extraction, which works well for structured SOPs and tables but does not parse scanned engineering blueprints or CAD drawings.
* **Static Prebuilt Index:** Adding new PDFs currently requires running `ingest.py` and committing the updated index files rather than uploading documents dynamically through the UI.

### Planned Future Improvements
* **Active-Only Retrieval Filter:** Add a UI toggle to exclude `SUPERSEDED` documents at the FAISS filtering stage by default while keeping them accessible for ISO audit comparisons.
* **Admin Document Upload Pipeline:** Add an authenticated upload endpoint backed by persistent object storage to ingest new SOP revisions without redeploying.
* **Multimodal Blueprint Parsing & Semantic Caching:** Support vision-based table/diagram parsing and cache frequent shop-floor alarm queries to reduce API latency and rate-limit exposure.