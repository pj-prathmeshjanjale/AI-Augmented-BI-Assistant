# 📊 Enterprise AI BI Assistant — Industry-Grade Natural Language Data Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Groq AI](https://img.shields.io/badge/LLM-Groq%20GPT--OSS--20B-7c3aed.svg)](https://groq.com/)
[![Chart.js](https://img.shields.io/badge/Visuals-Chart.js%20v3-ff6384.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, natural language **Business Intelligence & Text-to-SQL Platform**. Ask questions in plain English or voice, and automatically generate SQL queries, executive summaries, KPI metrics, dynamic data tables, and interactive Power BI-style charts.

---

## ✨ Features

- 🧠 **Dual-Mode Intent Router**: Automatically distinguishes conversational chat (*"hello"*, *"explain AI"*) from data analytics queries (*"top 5 products"*), preventing unnecessary database queries.
- 🎛️ **Multi-CSV Library Manager**: Upload and save multiple CSV datasets simultaneously (*e.g., Kaggle datasets, sales reports*) with persistent registry tracking and 1-click dataset switching.
- 🗑️ **1-Click Dataset Deletion**: Remove unwanted CSV datasets from your library directly from the web interface.
- 🏥 **Automated Dataset Health Inspector**: Diagnostic scanning on CSV upload evaluating total rows, missing data cells, column data types, and an overall Data Quality Score.
- 🎯 **Dynamic Context-Aware Presets**: Recommended question buttons automatically update based on the active dataset schema (*MySQL vs CSV*).
- 📊 **Power BI-Style Visual Toolbar**: Customize charts on the fly with chart type switching (*Bar, Line, Pie/Donut*), color themes (*Indigo, Emerald, Sunset, Neon*), sorting (*High-to-Low, Low-to-High*), and PNG image downloads.
- 📄 **Executive PDF Summary Exporter**: 1-click A4 print-ready PDF summary report generator.
- 🎙️ **Hands-Free Voice Input**: Web Speech API integration transcribes spoken questions directly.
- 🛡️ **Strict SQL Security Guardrails**: Enforces read-only `SELECT`/`WITH` queries, blocking multi-statement execution and destructive SQL keywords (`DROP`, `DELETE`, `UPDATE`).

---

## 🏗️ Architecture & Tech Stack

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3, Chart.js v3+, FontAwesome 6, Web Speech API.
- **Backend**: FastAPI (Python), Uvicorn ASGI Server.
- **LLM Engine**: Groq API (`openai/gpt-oss-20b` with `groq/compound` fallback).
- **Databases**: MySQL (`business_db`) + SQLite (`uploaded_dataset.db`).

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- MySQL Server (`business_db` schema)

### 2. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/AI_BI_Assistant.git
cd AI_BI_Assistant

# Install Python dependencies
pip install fastapi uvicorn mysql-connector-python python-dotenv groq requests python-multipart
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=business_db
```

### 4. Run the Backend Server
```bash
python -m uvicorn app.main:app --reload
```

### 5. Launch the Web Dashboard
Open `frontend/index.html` in Chrome or Edge!

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
