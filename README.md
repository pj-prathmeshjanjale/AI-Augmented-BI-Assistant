# 📊 Enterprise AI BI Assistant — Autonomous Natural Language Data Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Groq AI](https://img.shields.io/badge/LLM-Groq%20GPT--OSS--120B-7c3aed.svg)](https://groq.com/)
[![Chart.js](https://img.shields.io/badge/Visuals-Chart.js%20v3-ff6384.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-success.svg)](https://ai-bi-assistant-olive.vercel.app/)

An enterprise-grade, natural language **Business Intelligence & Text-to-SQL Platform**. Ask business questions in plain English or voice, automatically generating read-only SQL queries, executive summaries, KPI metric cards, dynamic data tables, visual charts, predictive AI trend forecasts, and 1-click interactive drill-downs.

---

## 🔗 Live Demo Links

- 🌐 **Web Dashboard (Vercel)**: [https://ai-bi-assistant-olive.vercel.app/](https://ai-bi-assistant-olive.vercel.app/)
- ⚡ **Backend API (Render)**: [https://ai-bi-assistant-vz0b.onrender.com](https://ai-bi-assistant-vz0b.onrender.com)
- 🐙 **GitHub Repository**: [https://github.com/pratikmalik/AI_BI_Assistant.git](https://github.com/pratikmalik/AI_BI_Assistant.git)

---

## 🌟 Key Features

- 🧠 **Dual-Mode Intent Router & Reasoning Sanitizer**: Distinguishes conversational chat (*"hello"*, *"explain AI"*) from data analytics queries (*"top 5 products"*). Automatically strips DeepSeek/Qwen `<think> ... </think>` reasoning tags before SQL validation.
- 🔮 **Predictive AI Trend Forecasting Engine**: Uses Linear Regression ($y = mx + b$) to project future 3-period trends, displaying purple prediction bars (`#8b5cf6`) and executive growth rate badges.
- 🎯 **Interactive Chart & Data Table Drill-Downs**: 1-click drill-down filtering on any chart bar/slice or data table cell to query granular transaction records instantly.
- 💡 **Dynamic Column-Tailored Question Generator**: Automatically inspects numeric vs. text/categorical columns of any active CSV or MySQL database to generate 100% relevant recommended question chips.
- 🔒 **Single-Question Lockout Guard**: Disables input fields, Send button, preset chips, and drill-down clicks while an AI answer is processing to prevent double-submissions and race conditions.
- 🗄️ **Dual Execution Engine with Cloud Fallback**: Runs natively against local MySQL (`business_db`) or falls back to an embedded 3.3MB SQLite database (`backend/default_business.db`) for 100% live cloud demo execution.
- 🎛️ **Multi-CSV Library Manager**: Stream-ingest, save, and switch between multiple CSV datasets simultaneously with persistent registry tracking.
- 🏥 **Automated Dataset Health Inspector**: Diagnostic scanning on CSV upload evaluating total rows, missing data cells, column data types, and an overall Data Quality Score (*0% to 100%*).
- 📊 **Power BI-Style Visual Toolbar**: Customize charts on the fly with chart type switching (*Bar, Line, Pie/Donut*), color themes (*Indigo, Emerald, Sunset, Neon*), sorting (*High-to-Low, Low-to-High*), Excel (`.xlsx`) downloads, and Executive PDF print previews.
- 🛡️ **Strict SQL Security Guardrails**: Enforces read-only `SELECT`/`WITH` queries, blocking multi-statement execution and destructive SQL keywords (`DROP`, `DELETE`, `UPDATE`, `ALTER`, `TRUNCATE`).

---

## 📂 Project Structure

```
AI_BI_Assistant/
│
├── 🟢 backend/                    # FastAPI Backend API Server
│   ├── app/
│   │   ├── ai/                    # Intent router, SQL generator, answer synthesis, Groq client
│   │   ├── database/              # MySQL & SQLite connection & query executors
│   │   └── main.py                # FastAPI Application Entry Point
│   ├── default_business.db        # 3.3MB Pre-seeded cloud database (10 tables, 5000+ rows)
│   ├── requirements.txt           # Python dependencies list
│   └── uploaded_dataset.db        # Persistent SQLite Multi-CSV library
│
├── 🔵 frontend/                   # Web Dashboard UI
│   ├── index.html                 # Self-contained Web BI Dashboard UI
│   └── js/
│       └── chart.umd.js           # Chart.js library
│
├── default_business.db            # Root pre-seeded database fallback
├── .gitignore                     # Git exclusion rules
└── README.md                      # GitHub Repository Documentation
```

---

## ⚡ Quick Start & Running Commands

### 1. Prerequisites
- Python 3.10+
- MySQL Server (`business_db` schema - optional for local PC, cloud uses embedded SQLite)

### 2. Clone & Install Dependencies
```bash
git clone https://github.com/pratikmalik/AI_BI_Assistant.git
cd AI_BI_Assistant/backend

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file inside `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=business_db
```

### 4. Running the Application

#### 🟢 Step A: Start Backend API Server
Open Terminal 1:
```bash
cd backend
python -m uvicorn app.main:app --reload
```
*Backend API will run at:* `http://127.0.0.1:8000`

#### 🔵 Step B: Start Frontend Web Dashboard
Open Terminal 2:
```bash
cd frontend
python -m http.server 3000
```
*Frontend UI will run at:* `http://localhost:3000`

*(Or open `frontend/index.html` directly in Chrome/Edge!)*

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/ask` | Main query endpoint (Dual-mode intent routing, Text-to-SQL, Answer synthesis) |
| `GET` | `/datasets` | Returns list of available datasets & dynamic recommended questions |
| `POST` | `/switch_dataset` | Switches active query engine between MySQL and saved CSVs |
| `DELETE` | `/delete_dataset/{id}` | Drops a CSV table from memory and updates library registry |
| `POST` | `/upload_csv` | Ingests a new CSV dataset into the library & runs health inspection |
| `GET` | `/csv_health` | Returns detailed data quality stats for active CSV dataset |
| `GET` | `/health` | API health check and active session tracking |

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
