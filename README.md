<div align="center">

# 🤖 AI-Augmented BI Assistant

### Enterprise Natural Language Business Intelligence & Text-to-SQL Analytics Platform

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-Vercel-000000?style=for-the-badge&logo=vercel)](https://ai-augmented-bi-assistant.vercel.app/)
[![API Docs](https://img.shields.io/badge/⚡%20API%20Docs-Render-46E3B7?style=for-the-badge&logo=render)](https://ai-augmented-bi-assistant.onrender.com/docs)
[![GitHub](https://img.shields.io/badge/Source-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/pj-prathmeshjanjale/AI-Augmented-BI-Assistant)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C?logo=chainlink&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Store-FF6B35)
![Groq](https://img.shields.io/badge/Groq%20AI-LLM%20Provider-7C3AED)
![Chart.js](https://img.shields.io/badge/Chart.js-Visualizations-FF6384?logo=chartdotjs&logoColor=white)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)
![MIT License](https://img.shields.io/badge/License-MIT-22C55E)

</div>

---

## 📌 What Is This?

**AI-Augmented BI Assistant** is a production-deployed, full-stack AI platform that lets business users ask data questions in plain English or voice — and instantly receive SQL queries, executive summaries, KPI cards, and interactive charts.

> **"Ask 'What was last month's revenue by region?' and get a live bar chart, a data table, and a CEO-ready summary in under 3 seconds."**

| | |
|--|--|
| 🌐 **Live Frontend** | https://ai-augmented-bi-assistant.vercel.app/ |
| ⚡ **Live API** | https://ai-augmented-bi-assistant.onrender.com/docs |
| 💻 **Tech Stack** | FastAPI · LangChain LCEL · FAISS · Groq AI · MySQL/SQLite · Chart.js |
| 📊 **Dataset** | 10-table relational schema · 5,000 customers · 50,000+ order items |
| 📐 **Codebase** | 6,300+ lines across 30 source files |

---

## 🎬 Demo

> **Try these queries on the [live site](https://ai-augmented-bi-assistant.vercel.app/):**

| Query | What You Get |
|-------|-------------|
| `region wise revenue` | Bar chart + revenue table by region |
| `top 5 most sale product` | Ranked product table + horizontal bar chart |
| `compare last 2 month revenue` | Month-over-month comparison with trend line |
| `monthly sales trend` | 12-month line chart with projections |
| `which category has highest revenue` | Doughnut chart + executive summary |
| `hello` | Conversational AI response (no SQL executed) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vercel)                            │
│  index.html · Chart.js · Voice Input · CSV Upload · PDF Export      │
└───────────────────────────┬─────────────────────────────────────────┘
                            │  POST /ask  (JSON)
┌───────────────────────────▼─────────────────────────────────────────┐
│                   FASTAPI BACKEND (Render)                           │
│                                                                     │
│  ┌─────────────────┐    ┌──────────────────────────────────────┐   │
│  │  Intent Router  │    │        RAG Pipeline (LangChain)      │   │
│  │                 │    │                                      │   │
│  │ Conversational ─┼──► │  Query ──► FAISS Search ──► Top-K   │   │
│  │ Analytics      ─┼──► │  Docs  ──► ChatPromptTemplate       │   │
│  └─────────────────┘    │         ──► Groq LLM                │   │
│                         │         ──► StrOutputParser ──► SQL  │   │
│                         └──────────────────┬─────────────────-┘   │
│                                            │                       │
│  ┌─────────────────────────────────────────▼───────────────────┐   │
│  │              SQL Security Guardrails (2-Stage)               │   │
│  │  validate_sql() ──► strict_security_guardrail()             │   │
│  │  Blocks: DROP / DELETE / UPDATE / multi-statement           │   │
│  └─────────────────────────────────────────┬───────────────────┘   │
│                                            │                       │
│  ┌─────────────────────────────────────────▼───────────────────┐   │
│  │             Smart Query Execution Engine                     │   │
│  │  MySQL (primary) ──► SQLite fallback ──► Auto-repair LLM   │   │
│  └─────────────────────────────────────────┬───────────────────┘   │
│                                            │                       │
│  Answer Generator ──► Chart Builder ──► JSON Response              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 🧠 RAG-Powered Text-to-SQL Engine
- **LangChain LCEL pipeline**: `ChatPromptTemplate → Groq LLM → StrOutputParser`
- **FAISS vector similarity search**: retrieves only relevant table schemas, join paths, and KPI formulas — no full schema injection (prevents context overflow)
- **25 curated domain documents**: table schemas, FK join paths, KPI formulas, SQL templates
- **Lightweight embeddings**: custom TF-IDF embeddings (<5MB RAM) replace sentence-transformers (350MB), enabling Render free-tier deployment

### 🔄 Dual-Mode Intent Router
- **Conversational mode**: handles `hello`, general knowledge, and out-of-scope questions without touching the database
- **Analytics mode**: routes structured business questions through the full RAG → SQL → Execute → Visualize pipeline

### 🗄️ Dual Database Engine with Auto-Failover
- **Primary**: MySQL `business_db` (10 relational tables)
- **Cloud fallback**: embedded `default_business.db` SQLite (3.2MB, 50K+ rows) — auto-detected when MySQL is unavailable
- **MySQL → SQLite dialect translation**: `DATE_FORMAT()` → `strftime()`, `IFNULL()` → `COALESCE()`, `CURDATE()` → dynamic max date
- **Self-healing SQL**: on execution failure, LLM auto-repairs the query and retries

### 🛡️ Two-Stage SQL Security Guardrails
- Blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `GRANT`, `REVOKE`
- Prevents multi-statement injection (`;` chaining)
- Blocks stored procedure execution (`xp_cmdshell`, `exec sp_`)
- **100% block rate on 7/7 security test payloads**

### 📊 Power BI-Style Interactive Dashboard
- 4 chart types: Vertical Bar, Horizontal Bar, Line, Doughnut/Pie
- 4 color themes: Indigo, Emerald, Sunset, Neon
- Drill-down filtering, trend projections ($y = mx + b$)
- Export: Excel `.xlsx`, CSV, PNG chart image, printable PDF report

### 🎤 Voice Input & CSV Dataset Manager
- Browser Web Speech API for hands-free voice queries
- Upload arbitrary CSV files → auto-ingested to isolated SQLite tables
- Automated data quality health inspector (row count, missing values, data quality score)
- Per-session CSV dataset isolation (no cross-user contamination)

---

## 📁 Project Structure

```
AI-Augmented-BI-Assistant/
├── backend/                          # FastAPI Python backend
│   ├── app/
│   │   ├── ai/                      # LLM & intelligence layer
│   │   │   ├── groq_client.py       # Groq SDK client
│   │   │   ├── llm_provider.py      # Multi-provider LLM factory
│   │   │   ├── intent_router.py     # Conversational vs analytics router
│   │   │   ├── answer_generator.py  # Executive business answer synthesis
│   │   │   ├── chart_detector.py    # Visualization applicability detection
│   │   │   ├── chart_generator.py   # Chart.js data structure builder
│   │   │   ├── clarification.py     # Ambiguous query handler
│   │   │   ├── sql_generator.py     # Text-to-SQL entry point
│   │   │   ├── sql_validator.py     # SQL safety validator
│   │   │   └── result_formatter.py  # Query result formatter
│   │   │
│   │   ├── rag/                     # LangChain + FAISS RAG subsystem
│   │   │   ├── documents.py         # 25 curated domain knowledge docs
│   │   │   ├── embeddings.py        # Lightweight TF-IDF embedding model
│   │   │   ├── vector_store.py      # FAISS index management & persistence
│   │   │   ├── retriever.py         # Semantic context retriever
│   │   │   ├── rag_chain.py         # LangChain LCEL RAG chain
│   │   │   ├── observability.py     # RAG telemetry & latency logging
│   │   │   ├── evaluate_rag.py      # Benchmark evaluation suite
│   │   │   └── faiss_index/         # Pre-built FAISS index (committed)
│   │   │       ├── index.faiss
│   │   │       └── index.pkl
│   │   │
│   │   ├── database/                # Database layer
│   │   │   ├── connection.py        # MySQL connection factory
│   │   │   ├── query_executor.py    # Validated query runner
│   │   │   ├── schema_loader.py     # Dynamic INFORMATION_SCHEMA reader
│   │   │   └── default_db_seeder.py # SQLite seeder for cloud fallback
│   │   │
│   │   └── main.py                  # FastAPI app, all endpoints, lifecycle
│   │
│   ├── default_business.db          # Pre-seeded 3.2MB SQLite database
│   └── requirements.txt             # Python dependencies
│
├── frontend/
│   └── index.html                   # Full single-page BI dashboard (2,400+ lines)
│
├── render.yaml                      # Render deployment configuration
├── .env.example                     # Environment variable template
└── README.md
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- MySQL Server *(optional — SQLite fallback works automatically)*

### 1. Clone & Install
```bash
git clone https://github.com/pj-prathmeshjanjale/AI-Augmented-BI-Assistant.git
cd AI-Augmented-BI-Assistant/backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp ../.env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here   # Get free at console.groq.com

# Optional MySQL (SQLite fallback used automatically if not set)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=business_db
```

### 3. Run Backend
```bash
uvicorn app.main:app --reload --port 8000
```
API docs → http://127.0.0.1:8000/docs

### 4. Open Dashboard
```bash
cd ../frontend
python -m http.server 3000
```
Dashboard → http://localhost:3000

---

## 🌐 Production Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel (auto-deploy from `main`) | https://ai-augmented-bi-assistant.vercel.app/ |
| Backend API | Render (free tier, `backend/` root) | https://ai-augmented-bi-assistant.onrender.com |

### Render Environment Variables Required
| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key |
| `DB_HOST` | MySQL host (optional) |
| `DB_USER` | MySQL username (optional) |
| `DB_PASSWORD` | MySQL password (optional) |
| `DB_NAME` | MySQL database name (optional) |

> **Note**: Render free tier spins down after 15min inactivity. First request may take ~30–60s to cold-start. Subsequent requests run in 1–3s.

---

## 📊 Benchmark Results

Evaluated against `default_business.db` (10 tables, 50,000+ rows):

| Metric | Result |
|--------|--------|
| SQL Validity Rate | **100% (8/8)** |
| SQL Safety Rate | **100% (8/8)** |
| Execution Success Rate | **100% (8/8)** |
| Semantic Correctness | **100% (8/8)** |
| Security Block Rate | **100% (7/7 attack payloads)** |
| FAISS Retrieval Latency | **~44ms median** |
| End-to-End Response Time | **~1–3s (Groq API)** |

### Sample Validated Queries

| Question | Generated SQL Pattern | Result |
|----------|----------------------|--------|
| *"Total revenue across all orders?"* | `SELECT SUM(quantity * unit_price) FROM order_items` | $7.94B ✅ |
| *"Which region has highest revenue?"* | 4-table JOIN with GROUP BY region | North: $1.51B ✅ |
| *"Top 5 customers by spending?"* | 3-table JOIN, ORDER BY total_spent DESC LIMIT 5 | Customer #4490 ✅ |
| *"Monthly sales trend?"* | DATE_FORMAT grouping + chronological ORDER | 12-month series ✅ |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ask` | Main NL→SQL→answer pipeline |
| `GET` | `/health` | Health check + session status |
| `GET` | `/datasets` | List available datasets |
| `POST` | `/upload_csv` | Upload & ingest CSV dataset |
| `POST` | `/switch_dataset` | Switch active data source |
| `GET` | `/csv_health` | Data quality report for active CSV |
| `POST` | `/rag/rebuild` | Rebuild FAISS vector index |
| `GET` | `/rag/telemetry` | RAG latency & retrieval telemetry |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq API (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`) |
| **RAG Framework** | LangChain LCEL (`ChatPromptTemplate → LLM → StrOutputParser`) |
| **Vector Store** | FAISS CPU (pre-built, committed to repo) |
| **Embeddings** | Custom TF-IDF (numpy, zero model loading, <5MB RAM) |
| **Backend** | FastAPI + Uvicorn (Python 3.10+) |
| **Database** | MySQL (primary) + SQLite (auto-fallback, 3.2MB embedded) |
| **Frontend** | Vanilla HTML/CSS/JS + Chart.js |
| **Deployment** | Vercel (frontend) + Render (backend) |
| **Data Export** | SheetJS (Excel), html2pdf.js (PDF), Canvas API (PNG) |

---

## 📄 License

Distributed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ by [Prathamesh Janjale](https://github.com/pj-prathmeshjanjale)**

[🌐 Live Demo](https://ai-augmented-bi-assistant.vercel.app/) · [⚡ API Docs](https://ai-augmented-bi-assistant.onrender.com/docs) · [📂 Source Code](https://github.com/pj-prathmeshjanjale/AI-Augmented-BI-Assistant)

</div>
