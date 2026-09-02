<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=28&duration=3000&pause=1000&color=2563EB&center=true&vCenter=true&width=800&lines=AI-Augmented+BI+Assistant;Natural+Language+%E2%86%92+SQL+%E2%86%92+Insights;Ask+Data+Questions+in+Plain+English" alt="Typing SVG" />

<br/>

**Enterprise-grade Business Intelligence platform powered by LangChain RAG · Groq AI · FAISS · FastAPI**

<br/>

[![Live Demo](https://img.shields.io/badge/%F0%9F%8C%90%20Live%20Demo-Visit%20Now-2563EB?style=for-the-badge)](https://ai-augmented-bi-assistant.vercel.app/)&nbsp;
[![API Docs](https://img.shields.io/badge/%E2%9A%A1%20API%20Docs-Swagger%20UI-009688?style=for-the-badge)](https://ai-augmented-bi-assistant.onrender.com/docs)&nbsp;
[![GitHub Stars](https://img.shields.io/github/stars/pj-prathmeshjanjale/AI-Augmented-BI-Assistant?style=for-the-badge&color=F59E0B)](https://github.com/pj-prathmeshjanjale/AI-Augmented-BI-Assistant)

<br/>

![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white)&nbsp;
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)&nbsp;
![LangChain](https://img.shields.io/badge/LangChain_LCEL-1C3C3C?style=flat-square)&nbsp;
![FAISS](https://img.shields.io/badge/FAISS_Vector_DB-FF6B35?style=flat-square)&nbsp;
![Groq](https://img.shields.io/badge/Groq_AI-7C3AED?style=flat-square)&nbsp;
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)&nbsp;
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)&nbsp;
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat-square&logo=chartdotjs&logoColor=white)&nbsp;
![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)&nbsp;
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black)&nbsp;
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)

</div>

---

## 📌 Overview

**AI-Augmented BI Assistant** converts plain English (or voice) business questions into SQL queries, executes them against a relational database, and returns executive summaries, KPI cards, and interactive charts — all in real time.

> *"Ask 'Compare last 2 months revenue by region' and receive a live bar chart, a formatted data table, and a CEO-ready written insight in under 3 seconds."*

No SQL knowledge required. No static dashboards. Ask anything about your data.

---

## 🚀 Try It Live

| | Link |
|--|--|
| 🌐 **Web Dashboard** | https://ai-augmented-bi-assistant.vercel.app/ |
| ⚡ **REST API + Swagger** | https://ai-augmented-bi-assistant.onrender.com/docs |
| 📂 **Source Code** | https://github.com/pj-prathmeshjanjale/AI-Augmented-BI-Assistant |

> **Note:** Render free tier sleeps after 15 min of inactivity. First request may take ~30–60s cold start. Subsequent requests respond in 1–3s.

**Quick test queries to run on the live site:**
```
region wise revenue
top 5 most sale product
compare last 2 month revenue
which category has highest revenue
monthly sales trend
hello                          ← tests conversational AI mode (no SQL executed)
DROP TABLE orders              ← tests security guardrails (blocked)
```

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     WEB DASHBOARD  (Vercel)                          │
│           HTML · CSS · Chart.js · Voice API · CSV Upload             │
└─────────────────────────────┬────────────────────────────────────────┘
                              │  POST /ask
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND  (Render)                        │
│                                                                      │
│  ┌────────────────┐    ┌──────────────────────────────────────────┐  │
│  │  Intent Router │    │           RAG Pipeline                   │  │
│  │                │    │                                          │  │
│  │  Conversational├───►│  Question                                │  │
│  │  Analytics     ├───►│    └─► FAISS Similarity Search          │  │
│  └────────────────┘    │         └─► Top-K Knowledge Docs        │  │
│                        │               └─► ChatPromptTemplate    │  │
│                        │                     └─► Groq LLM        │  │
│                        │                           └─► SQL Query  │  │
│                        └──────────────────┬───────────────────────┘  │
│                                           │                          │
│               ┌───────────────────────────▼────────────────────────┐ │
│               │           SQL Security Guardrails                   │ │
│               │   Blocks: DROP · DELETE · UPDATE · Multi-statement  │ │
│               └───────────────────────────┬────────────────────────┘ │
│                                           │                          │
│               ┌───────────────────────────▼────────────────────────┐ │
│               │         Smart Query Execution Engine                │ │
│               │  MySQL Primary → SQLite Fallback → LLM Auto-repair  │ │
│               └───────────────────────────┬────────────────────────┘ │
│                                           │                          │
│          Answer Generator · Chart Builder · Observability Telemetry  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

<details>
<summary><b>🧠 RAG-Powered Text-to-SQL Engine</b></summary>
<br/>

- **LangChain LCEL pipeline**: `ChatPromptTemplate → Groq LLM → StrOutputParser`
- **FAISS vector similarity search** retrieves only the relevant table schemas, FK join paths, and KPI formulas per query — no full-schema injection, no context overflow
- **25 curated domain documents**: 10 table schemas, 5 join paths, 4 KPI formulas, 6 SQL templates
- **Lightweight TF-IDF embeddings** (custom numpy implementation, <5MB RAM) replace sentence-transformers (350MB), enabling Render free-tier deployment

</details>

<details>
<summary><b>🔄 Dual-Mode Intent Router</b></summary>
<br/>

- **Conversational mode**: handles greetings and general knowledge without touching the database
- **Analytics mode**: routes structured business questions through the full RAG → SQL → Execute → Visualize pipeline
- Classification uses `openai/gpt-oss-20b` (avg <200ms) with keyword short-circuits for common patterns

</details>

<details>
<summary><b>🗄️ Dual Database Engine with Auto-Failover</b></summary>
<br/>

- **Primary**: MySQL `business_db` (10 relational tables)
- **Cloud fallback**: embedded `default_business.db` SQLite (3.2MB, 50K+ rows) — auto-detected when MySQL is unavailable
- **MySQL → SQLite dialect translation** at runtime: `DATE_FORMAT()` → `strftime()`, `IFNULL()` → `COALESCE()`, `CURDATE()` → dynamic max date
- **Self-healing SQL**: on execution failure, LLM auto-repairs the query and retries

</details>

<details>
<summary><b>🛡️ Two-Stage SQL Security Guardrails</b></summary>
<br/>

- Blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `GRANT`, `REVOKE`
- Prevents multi-statement injection via `;` chaining
- Blocks stored procedure execution (`xp_cmdshell`, `exec sp_`)
- **100% block rate on all 7 security test attack payloads** (validated in `evaluate_rag.py`)

</details>

<details>
<summary><b>📊 Power BI-Style Interactive Dashboard</b></summary>
<br/>

- 4 chart types: Vertical Bar, Horizontal Bar, Line, Doughnut/Pie
- 4 color themes: Indigo, Emerald, Sunset, Neon
- Drill-down row filtering and trend projection overlays
- Export to: Excel `.xlsx` (SheetJS), CSV, PNG chart image, printable PDF report

</details>

<details>
<summary><b>🎤 Voice Input & Multi-CSV Dataset Manager</b></summary>
<br/>

- Browser Web Speech API for hands-free voice queries
- Upload arbitrary CSV files → auto-ingested to isolated SQLite session tables
- Automated health inspector: row count, column types, missing values, data quality score (0–100%)
- Per-session dataset isolation — no cross-user data contamination

</details>

---

## 📁 Project Structure

```
AI-Augmented-BI-Assistant/
│
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── ai/                       # Intelligence layer
│   │   │   ├── groq_client.py        # Groq SDK client
│   │   │   ├── llm_provider.py       # Multi-provider LLM factory
│   │   │   ├── intent_router.py      # Conversational vs analytics router
│   │   │   ├── answer_generator.py   # Executive answer synthesis
│   │   │   ├── chart_detector.py     # Visualization applicability
│   │   │   ├── chart_generator.py    # Chart.js data builder
│   │   │   ├── clarification.py      # Ambiguous query handler
│   │   │   ├── sql_validator.py      # SQL safety validator
│   │   │   └── result_formatter.py   # Query result formatter
│   │   │
│   │   ├── rag/                      # LangChain + FAISS RAG subsystem
│   │   │   ├── documents.py          # 25 curated domain knowledge docs
│   │   │   ├── embeddings.py         # Lightweight TF-IDF embedding model
│   │   │   ├── vector_store.py       # FAISS index management
│   │   │   ├── retriever.py          # Semantic context retriever
│   │   │   ├── rag_chain.py          # LangChain LCEL chain
│   │   │   ├── observability.py      # RAG telemetry logging
│   │   │   ├── evaluate_rag.py       # Benchmark evaluation suite
│   │   │   └── faiss_index/          # Pre-built FAISS index (committed)
│   │   │
│   │   ├── database/                 # Database layer
│   │   │   ├── connection.py         # MySQL connection factory
│   │   │   ├── query_executor.py     # Validated query runner
│   │   │   ├── schema_loader.py      # INFORMATION_SCHEMA reader
│   │   │   └── default_db_seeder.py  # SQLite seeder
│   │   │
│   │   └── main.py                   # FastAPI app + all endpoints (1,300+ lines)
│   │
│   ├── default_business.db           # Pre-seeded 3.2MB SQLite (50K+ rows)
│   └── requirements.txt
│
├── frontend/
│   └── index.html                    # Single-page BI dashboard (2,400+ lines)
│
├── render.yaml                       # Render.com deployment config
└── .env.example                      # Environment variable template
```

---

## 🚀 Local Setup

**1. Clone & install**
```bash
git clone https://github.com/pj-prathmeshjanjale/AI-Augmented-BI-Assistant.git
cd AI-Augmented-BI-Assistant/backend
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp ../.env.example .env
```
```env
# Required — get a free key at console.groq.com
GROQ_API_KEY=gsk_your_key_here

# Optional — SQLite fallback works automatically without MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=business_db
```

**3. Start backend**
```bash
uvicorn app.main:app --reload --port 8000
# API docs → http://127.0.0.1:8000/docs
```

**4. Open dashboard**
```bash
cd ../frontend && python -m http.server 3000
# Dashboard → http://localhost:3000
```

---

## 🌐 Deployment

| Layer | Platform | Config |
|-------|----------|--------|
| Frontend | Vercel | Auto-deploys from `main` branch, serves `frontend/` |
| Backend | Render | `render.yaml` · root: `backend/` · start: `uvicorn app.main:app` |

**Required Render environment variables:**

| Key | Description |
|-----|-------------|
| `GROQ_API_KEY` | Groq API key (required) |
| `DB_HOST` | MySQL host (optional — SQLite fallback auto-activates) |
| `DB_USER` | MySQL username (optional) |
| `DB_PASSWORD` | MySQL password (optional) |
| `DB_NAME` | MySQL database name (optional) |

---

## 📊 Benchmark Evaluation

Run the full benchmark suite locally:
```bash
cd backend && python -m app.rag.evaluate_rag
```

**Results against `default_business.db` (10 tables, 50,000+ rows):**

| Metric | Score |
|--------|-------|
| SQL Validity Rate | **100% — 8 / 8** |
| SQL Safety Rate | **100% — 8 / 8** |
| Execution Success Rate | **100% — 8 / 8** |
| Semantic Correctness | **100% — 8 / 8** |
| Security Guardrail Block Rate | **100% — 7 / 7 attack payloads** |
| FAISS Retrieval Latency | **~44ms median** |
| End-to-End Response Time | **1 – 3s (Groq API)** |

**Sample validated queries:**

| Question | SQL Pattern | Ground Truth |
|----------|-------------|--------------|
| *"Total revenue across all orders?"* | `SELECT SUM(qty * price) FROM order_items` | **$7.94B** ✅ |
| *"Which region has highest revenue?"* | 4-table JOIN + GROUP BY | **North: $1.51B** ✅ |
| *"Top 5 customers by spending?"* | 3-table JOIN + ORDER BY DESC LIMIT 5 | **Customer #4490** ✅ |
| *"Monthly sales trend?"* | DATE_FORMAT GROUP BY + ORDER ASC | **12-month series** ✅ |
| *"Payment breakdown by method?"* | GROUP BY payment_method + % share | **Debit: $1.85B** ✅ |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ask` | Main NL→SQL→answer pipeline with optional `include_debug` |
| `GET` | `/health` | Health check, session count, active mode |
| `GET` | `/datasets` | List available datasets + recommended questions |
| `POST` | `/upload_csv` | Upload and ingest CSV dataset into session SQLite |
| `POST` | `/switch_dataset` | Switch active query engine (MySQL / CSV) |
| `GET` | `/csv_health` | Data quality report for active CSV |
| `POST` | `/rag/rebuild` | Rebuild FAISS vector index from knowledge documents |
| `GET` | `/rag/telemetry` | RAG retrieval latencies and telemetry records |

Full interactive reference: **https://ai-augmented-bi-assistant.onrender.com/docs**

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | Groq API (`gpt-oss-120b` / `gpt-oss-20b`) | SQL generation + answer synthesis |
| **RAG** | LangChain LCEL | Prompt management + chain orchestration |
| **Vector DB** | FAISS CPU | Schema & KPI similarity retrieval |
| **Embeddings** | Custom TF-IDF (numpy) | Zero model loading, <5MB RAM |
| **Backend** | FastAPI + Uvicorn | REST API, session management |
| **Database** | MySQL + SQLite fallback | Primary + cloud execution engine |
| **Frontend** | Vanilla JS + Chart.js | Interactive BI dashboard |
| **Export** | SheetJS + html2pdf.js | Excel, PDF, PNG export |
| **Frontend Hosting** | Vercel | CDN + auto-deploy |
| **Backend Hosting** | Render | Cloud Python runtime |

---

## 📄 License

Distributed under the **MIT License** — see [`LICENSE`](LICENSE) for details.

---

<div align="center">

**Built by [Prathamesh Janjale](https://github.com/pj-prathmeshjanjale)**

[🌐 Live Demo](https://ai-augmented-bi-assistant.vercel.app/) &nbsp;·&nbsp; [⚡ API Docs](https://ai-augmented-bi-assistant.onrender.com/docs) &nbsp;·&nbsp; [⭐ Star on GitHub](https://github.com/pj-prathmeshjanjale/AI-Augmented-BI-Assistant)

*If this project helped you, consider giving it a ⭐*

</div>
