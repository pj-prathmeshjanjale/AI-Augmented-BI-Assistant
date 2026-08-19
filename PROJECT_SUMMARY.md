# 🚀 Enterprise AI BI Assistant — Project Documentation & Presentation Guide

## 📌 Project Overview
**Enterprise AI BI Assistant** is an industry-grade, natural language Business Intelligence & Text-to-SQL platform built with **FastAPI**, **Groq AI (OpenAI GPT-OSS-20B)**, **MySQL**, **SQLite**, and **Vanilla JavaScript + Chart.js**.

The platform allows business users and data analysts to ask questions in plain English or voice, automatically generating SQL queries, executive summaries, KPI metrics, dynamic data tables, and interactive Power BI-style charts.

---

## 🌟 Key Features & Architecture

### 1. 🧠 Dual-Mode Intent Router
- **Conversational General AI Mode**: Handles greetings (*"hello"*, *"hi"*) and general knowledge questions (*"explain AI"*, *"how to write python code"*) using Groq AI directly without executing unnecessary database queries.
- **Data Analytics BI Mode**: Translates business questions into read-only SQL queries, executing against MySQL or CSV datasets.

### 2. 🎛️ Multi-CSV Library & Dataset Selector
- **1-Click Switching**: Seamlessly switch between the default **MySQL Database (`business_db`)** and **Uploaded CSV datasets**.
- **Library Manager**: Upload multiple CSV files (*e.g., Kaggle Olympics `DF_final_feature.csv`, Corporate Sales `company_sales_2024.csv`*) with persistent registry tracking.
- **Dataset Deletion**: Delete uploaded datasets anytime directly from the UI header dropdown.

### 3. 🎯 Dynamic Context-Aware Preset Chips
- Preset recommendation chips automatically transform based on the selected dataset:
  - **MySQL Mode**: *top 5 most sale product*, *region wise revenue*, *monthly sales trend*.
  - **CSV Mode**: *top 5 teams by medal*, *average weight by sport*, *top 5 team by gdp per capita*.

### 4. 🏥 Automated Dataset Health Inspector
- Scans uploaded CSV files and displays a diagnostic health card:
  - **Data Quality Score** (*e.g., 100% Complete*)
  - **Total Record Count & Column Breakdown**
  - **Missing Data Cell Count**

### 5. 📊 Power BI-Style Interactive Visual Controls
- **Chart Types**: Vertical Bar, Horizontal Bar, Line Graph, Pie/Donut.
- **Color Themes**: Corporate Indigo, Emerald Forest, Warm Sunset, Vibrant Neon.
- **Sorting**: High-to-Low, Low-to-High, Original order.
- **Image Export**: Download charts as high-resolution PNG images.

### 6. 📄 Executive PDF Report Exporter & CSV Table Export
- **PDF Report Exporter**: 1-click print styling (`@media print`) formats clean A4 printable executive summary reports.
- **CSV Data Table Export**: Download any query result table as a `.csv` file.

### 7. 🎙️ Web Speech Voice Question Input
- Hands-free voice recognition transcribes spoken questions into natural language queries automatically.

### 8. 🛡️ Strict SQL Security Guardrails
- Enforces read-only `SELECT` and `WITH` CTE statements.
- Blocks multi-statement execution (`;`) and destructive keywords (`DROP`, `DELETE`, `UPDATE`, `TRUNCATE`).

---

## 🛠️ How to Launch & Run

### 1. Start FastAPI Backend Server
```powershell
cd C:\Users\psmal\OneDrive\Desktop\AI_BI_Assistant
python -m uvicorn app.main:app --reload
```

### 2. Open Web Dashboard
Double click or open in browser:
```
C:\Users\psmal\OneDrive\Desktop\AI_BI_Assistant\frontend\index.html
```

---

## 🎙️ Presentation & Demo Script (2-Minute Demo)

1. **Introduction**:
   > *"Welcome to Enterprise AI BI Assistant—a natural language data analytics platform designed to bridge the gap between non-technical business users and complex databases."*

2. **Conversational vs Data Query Demo**:
   > *"First, notice our Dual-Mode Intent Router. If I say 'hello' or ask general questions, the AI responds naturally in chat without dumping database tables. But when I ask 'top 5 teams by medal' or 'monthly sales trend', it immediately generates SQL, synthesizes executive insights, and builds interactive charts."*

3. **Multi-Dataset & Library Demo**:
   > *"Using our Dataset Selector, we can switch between our MySQL e-commerce database and custom uploaded CSV datasets in 1 click. When we upload a new CSV, our Automated Dataset Health Inspector analyzes row counts, missing data, and data quality scores."*

4. **Power BI Chart Controls & PDF Export**:
   > *"Finally, users can customize visualizations on the fly—changing chart types, color themes, and sorting—and export executive PDF reports or download high-res PNG images for board meetings."*
