# 📊 Enterprise AI BI Assistant — Industry-Grade Natural Language Data Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Groq AI](https://img.shields.io/badge/LLM-Groq%20GPT--OSS--20B-7c3aed.svg)](https://groq.com/)
[![Chart.js](https://img.shields.io/badge/Visuals-Chart.js%20v3-ff6384.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, natural language **Business Intelligence & Text-to-SQL Platform**. Ask business questions in plain English or voice, automatically generating read-only SQL queries, executive summaries, KPI metrics, dynamic data tables, and interactive Power BI-style charts.

---

## 🌟 Key Features

- 🧠 **Dual-Mode Intent Router**: Distinguishes conversational chat (*"hello"*, *"explain AI"*) from data analytics queries (*"top 5 products"*), preventing unnecessary database queries.
- 🎛️ **Multi-CSV Library Manager**: Upload and save multiple CSV datasets simultaneously (*e.g., Kaggle datasets, sales reports*) with persistent registry tracking and 1-click dataset switching.
- 🗑️ **1-Click Dataset Deletion**: Remove unwanted CSV datasets from your library directly from the web interface.
- 🏥 **Automated Dataset Health Inspector**: Diagnostic scanning on CSV upload evaluating total rows, missing data cells, column data types, and an overall Data Quality Score (*0% to 100%*).
- 🎯 **Dynamic Context-Aware Presets**: Recommended question buttons automatically update based on the active dataset schema (*MySQL vs CSV*).
- 📊 **Power BI-Style Visual Toolbar**: Customize charts on the fly with chart type switching (*Bar, Line, Pie/Donut*), color themes (*Indigo, Emerald, Sunset, Neon*), sorting (*High-to-Low, Low-to-High*), and PNG image downloads.
- 📄 **Executive PDF Report Exporter & CSV Table Export**: 1-click A4 print-ready PDF summary report generator and raw data CSV downloads.
- 🎙️ **Hands-Free Voice Input**: Web Speech API integration transcribes spoken questions directly into queries.
- 🛡️ **Strict SQL Security Guardrails**: Enforces read-only `SELECT`/`WITH` queries, blocking multi-statement execution and destructive SQL keywords (`DROP`, `DELETE`, `UPDATE`).

---

## 📂 Project Structure

```
AI_BI_Assistant/
│
├── 🟢 backend/                    # FastAPI Backend API Server
│   ├── app/
│   │   ├── ai/                    # Intent router, SQL generator, answer synthesis
│   │   ├── database/              # MySQL & SQLite connection & query executors
│   │   └── main.py                # FastAPI Application Entry Point
│   ├── scripts/                   # Data seeding scripts
│   ├── tests/                     # Unit test suites
│   ├── requirements.txt           # Python dependencies list
│   └── uploaded_dataset.db        # Persistent SQLite Multi-CSV library
│
├── 🔵 frontend/                   # Web Dashboard UI
│   ├── index.html                 # Self-contained Web BI Dashboard UI
│   └── js/
│       └── chart.umd.js           # Chart.js library
│
├── .gitignore                     # Git exclusion rules
├── PROJECT_SUMMARY.md             # Executive Documentation & Demo Script
└── README.md                      # GitHub Repository Documentation
```

---

## ⚡ Quick Start & Running Commands

### 1. Prerequisites
- Python 3.10+
- MySQL Server (`business_db` schema)

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
| `GET` | `/datasets` | Returns list of available datasets (MySQL + saved CSV library) |
| `POST` | `/switch_dataset` | Switches active query engine between MySQL and saved CSVs |
| `DELETE` | `/delete_dataset/{id}` | Drops a CSV table from memory and updates library registry |
| `POST` | `/upload_csv` | Ingests a new CSV dataset into the library & runs health inspection |
| `GET` | `/csv_health` | Returns detailed data quality stats for active CSV dataset |
| `GET` | `/health` | API health check and active session tracking |

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
