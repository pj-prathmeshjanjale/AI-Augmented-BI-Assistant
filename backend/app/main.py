import os
import re
import csv
import io
import codecs
import sqlite3
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Imports from your application modules
from app.ai.chart_detector import should_generate_chart
from app.ai.chart_generator import generate_chart_data
from app.ai.clarification import get_clarification
from app.ai.sql_generator import generate_sql
from app.ai.sql_validator import validate_sql
from app.database.query_executor import execute_query
from app.ai.result_formatter import format_results
from app.ai.answer_generator import generate_business_answer
from app.ai.intent_router import classify_intent_and_answer


# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Enterprise AI BI Assistant",
    description="Natural Language Business Intelligence & Text-to-SQL Engine with Multi-CSV Library Manager",
    version="1.6.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ==========================================
# ==========================================
# USER SESSION ISOLATION ENGINE
# ==========================================

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

CSV_DB_PATH = "uploaded_dataset.db"
ACTIVE_DATASET_MODE = "csv" if os.path.exists(CSV_DB_PATH) else "mysql"
ACTIVE_CSV_TABLE = "uploaded_data"
ACTIVE_CSV_FILENAME = "DF_final_feature.csv" if os.path.exists(CSV_DB_PATH) else None

SESSION_ACTIVE_MODE: Dict[str, str] = {}
SESSION_ACTIVE_TABLE: Dict[str, str] = {}
SESSION_ACTIVE_FILENAME: Dict[str, str] = {}


def get_session_db_path(session_id: str) -> str:
    clean_id = re.sub(r'\W+', '_', session_id or "default_session")
    return os.path.join(SESSIONS_DIR, f"dataset_{clean_id}.db")


def get_session_active_mode(session_id: str) -> str:
    db_path = get_session_db_path(session_id)
    default_mode = "csv" if os.path.exists(db_path) else "mysql"
    return SESSION_ACTIVE_MODE.get(session_id, default_mode)


def get_session_active_table(session_id: str) -> str:
    return SESSION_ACTIVE_TABLE.get(session_id, "uploaded_data")


def get_session_active_filename(session_id: str) -> Optional[str]:
    return SESSION_ACTIVE_FILENAME.get(session_id, None)


# ==========================================
# REQUEST MODELS
# ==========================================

class QuestionRequest(BaseModel):
    question: str = Field(..., example="top 5 most sale product", description="Natural language business question")
    session_id: Optional[str] = Field("default_session", description="Unique session ID for multi-turn conversation memory")


class ClearSessionRequest(BaseModel):
    session_id: str


class SwitchDatasetRequest(BaseModel):
    mode: str  # "mysql" or "csv:table_name"
    session_id: Optional[str] = "default_session"


# ==========================================
# CONVERSATIONAL SESSION STORE
# ==========================================

SESSION_HISTORY: Dict[str, List[Dict[str, Any]]] = {}


def get_session_history(session_id: str) -> List[Dict[str, Any]]:
    return SESSION_HISTORY.get(session_id, [])


def save_session_turn(session_id: str, question: str, sql: Optional[str], answer: Optional[str]):
    if session_id not in SESSION_HISTORY:
        SESSION_HISTORY[session_id] = []
        
    SESSION_HISTORY[session_id].append({
        "question": question,
        "sql": sql,
        "answer": answer
    })

    if len(SESSION_HISTORY[session_id]) > 5:
        SESSION_HISTORY[session_id] = SESSION_HISTORY[session_id][-5:]


# ==========================================
# SQL SECURITY GUARDRAIL
# ==========================================

def strict_security_guardrail(sql_query: str) -> tuple[bool, str]:
    if not sql_query or not isinstance(sql_query, str):
        return False, "SQL query is empty or invalid type."

    cleaned_sql = sql_query.strip()
    uppercase_sql = cleaned_sql.upper()

    statements = [s.strip() for s in cleaned_sql.split(";") if s.strip()]
    if len(statements) > 1:
        return False, "Multi-statement SQL queries containing ';' are strictly prohibited."

    if not (uppercase_sql.startswith("SELECT") or uppercase_sql.startswith("WITH")):
        return False, "Only read-only SELECT and CTE (WITH) queries are permitted."

    FORBIDDEN_KEYWORDS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b", r"\bUPDATE\b", 
        r"\bINSERT\b", r"\bALTER\b", r"\bCREATE\b", r"\bREPLACE\b",
        r"\bGRANT\b", r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b", 
        r"\bINTO\b", r"\bLOCK\b", r"\bFLUSH\b", r"\bSHUTDOWN\b"
    ]

    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, uppercase_sql):
            keyword = pattern.replace(r"\b", "").replace("\\", "")
            return False, f"Unauthorized security violation: Dangerous keyword '{keyword}' detected."

    return True, "Query passed read-only security check."


# ==========================================
# SYSTEM & HEALTH ENDPOINTS
# ==========================================

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Enterprise AI BI Assistant API",
        "version": "1.6.0",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check(session_id: str = "default_session"):
    db_path = get_session_db_path(session_id)
    return {
        "status": "healthy",
        "session_id": session_id,
        "active_mode": get_session_active_mode(session_id),
        "active_table": get_session_active_table(session_id),
        "csv_dataset_available": os.path.exists(db_path),
        "active_csv_filename": get_session_active_filename(session_id),
        "conversational_memory": "active",
        "active_sessions": len(SESSION_HISTORY)
    }


@app.get("/datasets")
def list_datasets(session_id: str = "default_session"):
    """Returns all available datasets for this isolated user session."""
    db_path = get_session_db_path(session_id)
    active_mode = get_session_active_mode(session_id)
    active_table = get_session_active_table(session_id)
    active_filename = get_session_active_filename(session_id)

    datasets = [
        {"id": "mysql", "name": "🗄️ Default MySQL Database (business_db)", "active": active_mode == "mysql"}
    ]
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS csv_registry (id TEXT PRIMARY KEY, filename TEXT, table_name TEXT, rows INTEGER, cols INTEGER);")
            cursor.execute("SELECT id, filename, table_name FROM csv_registry")
            records = cursor.fetchall()
            conn.close()

            if not records:
                datasets.append({
                    "id": "csv:uploaded_data",
                    "name": f"📁 CSV: {active_filename or 'Uploaded Dataset'}",
                    "active": (active_mode == "csv")
                })
            else:
                for csv_id, fname, tbl_name in records:
                    is_active = (active_mode == "csv" and active_table == tbl_name)
                    datasets.append({
                        "id": f"csv:{tbl_name}",
                        "name": f"📁 CSV: {fname}",
                        "active": is_active
                    })
        except Exception as e:
            print("Error listing CSV library datasets:", e)

    return {
        "active_mode": active_mode,
        "active_table": active_table,
        "datasets": datasets
    }


@app.post("/switch_dataset")
def switch_dataset(request: SwitchDatasetRequest):
    """Switch active query engine between MySQL and any saved CSV table for this isolated session."""
    session_id = request.session_id or "default_session"
    db_path = get_session_db_path(session_id)
    target_mode = request.mode.strip()

    if target_mode.startswith("csv"):
        if not os.path.exists(db_path):
            raise HTTPException(status_code=400, detail="No CSV dataset available in your session. Please upload a CSV first.")
        
        parts = target_mode.split(":", 1)
        tbl_name = parts[1] if len(parts) > 1 else "uploaded_data"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS csv_registry (id TEXT PRIMARY KEY, filename TEXT, table_name TEXT, rows INTEGER, cols INTEGER);")
        cursor.execute("SELECT filename FROM csv_registry WHERE table_name = ?", (tbl_name,))
        row = cursor.fetchone()
        conn.close()

        SESSION_ACTIVE_MODE[session_id] = "csv"
        SESSION_ACTIVE_TABLE[session_id] = tbl_name
        SESSION_HISTORY[session_id] = []
        if row:
            SESSION_ACTIVE_FILENAME[session_id] = row[0]

        label = SESSION_ACTIVE_FILENAME.get(session_id) or tbl_name
        return {
            "success": True,
            "active_mode": "csv",
            "active_table": tbl_name,
            "message": f"Switched active dataset to CSV: {label}"
        }

    elif target_mode == "mysql":
        SESSION_ACTIVE_MODE[session_id] = "mysql"
        SESSION_ACTIVE_TABLE[session_id] = "uploaded_data"
        SESSION_ACTIVE_FILENAME[session_id] = None
        SESSION_HISTORY[session_id] = []
        return {
            "success": True,
            "active_mode": "mysql",
            "message": "Switched active dataset to MySQL Database (business_db)"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid dataset mode selection.")


@app.post("/delete_dataset/{dataset_id:path}")
@app.delete("/delete_dataset/{dataset_id:path}")
def delete_dataset(dataset_id: str, session_id: str = "default_session"):
    """Deletes an uploaded CSV dataset table from user's isolated session library."""
    db_path = get_session_db_path(session_id)

    if dataset_id == "mysql":
        raise HTTPException(status_code=400, detail="Cannot delete default MySQL system database.")

    tbl_name = dataset_id.replace("csv:", "").strip()

    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="No CSV library found for this session.")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT filename FROM csv_registry WHERE table_name = ? OR id = ?", (tbl_name, tbl_name))
        row = cursor.fetchone()
        deleted_filename = row[0] if row else tbl_name

        cursor.execute(f"DROP TABLE IF EXISTS `{tbl_name}`;")
        cursor.execute("DELETE FROM csv_registry WHERE table_name = ? OR id = ?", (tbl_name, tbl_name))
        
        if tbl_name == "uploaded_data":
            cursor.execute("DROP TABLE IF EXISTS uploaded_data;")

        conn.commit()
        
        cursor.execute("SELECT id, filename, table_name FROM csv_registry")
        remaining = cursor.fetchall()
        conn.close()

        active_tbl = get_session_active_table(session_id)
        if active_tbl == tbl_name or get_session_active_mode(session_id) == "csv":
            if remaining:
                SESSION_ACTIVE_MODE[session_id] = "csv"
                SESSION_ACTIVE_TABLE[session_id] = remaining[0][2]
                SESSION_ACTIVE_FILENAME[session_id] = remaining[0][1]
            else:
                SESSION_ACTIVE_MODE[session_id] = "mysql"
                SESSION_ACTIVE_TABLE[session_id] = "uploaded_data"
                SESSION_ACTIVE_FILENAME[session_id] = None

        return {
            "success": True,
            "message": f"Successfully deleted dataset '{deleted_filename}' from your session library.",
            "active_mode": get_session_active_mode(session_id)
        }
    except Exception as e:
        print("Delete dataset error:", e)
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(e)}")


@app.post("/clear_session")
def clear_session(request: ClearSessionRequest):
    if request.session_id in SESSION_HISTORY:
        del SESSION_HISTORY[request.session_id]
    return {"success": True, "message": f"Session {request.session_id} memory cleared."}


def inspect_dataset_health(rows: list, clean_headers: list, total_rows: int = None) -> dict:
    actual_total_rows = total_rows if total_rows is not None else len(rows)
    total_cols = len(clean_headers)
    total_cells = actual_total_rows * total_cols
    
    sample_rows = rows[:3000] if len(rows) > 3000 else rows
    sample_size = len(sample_rows)

    missing_count = 0
    column_stats = []

    for col_idx, col_name in enumerate(clean_headers):
        nulls = 0
        numeric_count = 0
        sample_val = "N/A"
        
        for row in sample_rows:
            if col_idx < len(row):
                val = str(row[col_idx]).strip()
                if val == "" or val.lower() in ["na", "null", "none", "nan"]:
                    nulls += 1
                else:
                    if sample_val == "N/A":
                        sample_val = val
                    try:
                        float(val.replace(",", "").replace("$", ""))
                        numeric_count += 1
                    except ValueError:
                        pass
            else:
                nulls += 1

        non_nulls = max(1, (sample_size - nulls))
        col_type = "Numeric" if (numeric_count / non_nulls) > 0.6 else "Text/Categorical"
        null_pct = round((nulls / max(1, sample_size)) * 100, 1)
        est_null_count = int((null_pct / 100.0) * actual_total_rows)

        column_stats.append({
            "column": col_name,
            "type": col_type,
            "null_count": est_null_count,
            "completeness_pct": round(100 - null_pct, 1),
            "sample_value": sample_val
        })
        missing_count += est_null_count

    overall_health = round(((total_cells - missing_count) / max(1, total_cells)) * 100, 1)

    return {
        "health_score": overall_health,
        "total_rows": actual_total_rows,
        "total_cols": total_cols,
        "total_cells": total_cells,
        "missing_cells": missing_count,
        "column_stats": column_stats
    }


@app.get("/csv_health")
def get_csv_health(session_id: str = "default_session"):
    """Generates health inspection stats for active SQLite CSV dataset in this session."""
    db_path = get_session_db_path(session_id)
    active_table = get_session_active_table(session_id)
    active_filename = get_session_active_filename(session_id)

    if not os.path.exists(db_path):
        raise HTTPException(status_code=400, detail="No active CSV dataset found for your session.")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info(`{active_table}`);")
        cols_info = cursor.fetchall()
        if not cols_info:
            cursor.execute("PRAGMA table_info(`uploaded_data`);")
            cols_info = cursor.fetchall()

        clean_headers = [c[1] for c in cols_info]

        cursor.execute(f"SELECT * FROM `{active_table}` LIMIT 3000;")
        sample_rows = [list(r) for r in cursor.fetchall()]

        cursor.execute(f"SELECT COUNT(*) FROM `{active_table}`;")
        total_count = cursor.fetchone()[0]
        conn.close()

        health_report = inspect_dataset_health(sample_rows, clean_headers, total_rows=total_count)
        health_report["filename"] = active_filename or "uploaded_dataset.csv"
        return health_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inspect CSV health: {str(e)}")


# ==========================================
# CSV UPLOAD & MULTI-LIBRARY INGESTION ENDPOINT
# ==========================================

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), session_id: str = "default_session"):
    db_path = get_session_db_path(session_id)
    
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    try:
        clean_tbl_name = "csv_tbl_" + re.sub(r'\W+', '_', file.filename.strip().lower()).strip('_')
        SESSION_ACTIVE_FILENAME[session_id] = file.filename
        SESSION_ACTIVE_TABLE[session_id] = clean_tbl_name
        SESSION_ACTIVE_MODE[session_id] = "csv"
        SESSION_HISTORY[session_id] = []

        # Wrap UploadFile.file in a UTF-8 text stream reader
        text_stream = codecs.getreader("utf-8-sig")(file.file)
        reader = csv.reader(text_stream)

        headers = next(reader, None)
        if not headers:
            raise HTTPException(status_code=400, detail="CSV file is empty.")

        # Ensure unique, valid SQL column names
        raw_clean_headers = [re.sub(r'\W+', '_', h.strip().lower()).strip('_') or 'col' for h in headers]
        clean_headers = []
        seen = {}
        for h in raw_clean_headers:
            if h in seen:
                seen[h] += 1
                clean_headers.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 0
                clean_headers.append(h)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"DROP TABLE IF EXISTS `{clean_tbl_name}`;")
        cursor.execute("DROP TABLE IF EXISTS uploaded_data;")

        col_defs = ", ".join([f"`{h}` TEXT" for h in clean_headers])
        cursor.execute(f"CREATE TABLE `{clean_tbl_name}` ({col_defs});")
        cursor.execute(f"CREATE TABLE uploaded_data ({col_defs});")

        placeholders = ", ".join(["?"] * len(clean_headers))
        insert_sql = f"INSERT INTO `{clean_tbl_name}` VALUES ({placeholders})"
        insert_sql_ud = f"INSERT INTO uploaded_data VALUES ({placeholders})"

        batch = []
        sample_rows = []
        row_count = 0
        
        for parsed in reader:
            if not parsed or not any(parsed):
                continue

            if len(parsed) < len(clean_headers):
                parsed += [""] * (len(clean_headers) - len(parsed))
            elif len(parsed) > len(clean_headers):
                parsed = parsed[:len(clean_headers)]

            batch.append(parsed)
            if len(sample_rows) < 2000:
                sample_rows.append(parsed)
            row_count += 1

            if len(batch) >= 5000:
                cursor.executemany(insert_sql, batch)
                cursor.executemany(insert_sql_ud, batch)
                batch = []

        if batch:
            cursor.executemany(insert_sql, batch)
            cursor.executemany(insert_sql_ud, batch)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS csv_registry (
                id TEXT PRIMARY KEY,
                filename TEXT,
                table_name TEXT,
                rows INTEGER,
                cols INTEGER
            );
        """)
        cursor.execute("INSERT OR REPLACE INTO csv_registry VALUES (?, ?, ?, ?, ?)",
                       (clean_tbl_name, file.filename, clean_tbl_name, row_count, len(clean_headers)))
        
        conn.commit()
        conn.close()

        health_report = inspect_dataset_health(sample_rows, clean_headers, total_rows=row_count)

        return {
            "success": True,
            "filename": file.filename,
            "message": f"Successfully ingested '{file.filename}' ({row_count:,} rows) into active CSV Library!",
            "rows": row_count,
            "columns": clean_headers,
            "table_name": clean_tbl_name,
            "health": health_report
        }

    except Exception as e:
        print("CSV STREAM UPLOAD ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to stream ingest CSV: {str(e)}")


def get_default_db_path() -> str:
    possible_paths = [
        "default_business.db",
        os.path.abspath("default_business.db"),
        os.path.join(os.path.dirname(__file__), "..", "..", "default_business.db"),
        os.path.join(os.path.dirname(__file__), "..", "default_business.db"),
        os.path.join(os.path.dirname(__file__), "default_business.db")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    try:
        from app.database.default_db_seeder import seed_default_business_db
        seed_default_business_db()
        return "default_business.db"
    except Exception as seed_err:
        print("Seeder error:", seed_err)
        return "default_business.db"


@app.on_event("startup")
def startup_event():
    get_default_db_path()


def convert_mysql_sql_to_sqlite(sql: str, db_path: str = None) -> str:
    """Translates MySQL date functions and keywords into SQLite compatible equivalents."""
    s = sql

    target_db = db_path or get_default_db_path()

    # Dynamically find max date in orders table if present, default to 2026-08-09
    max_date = "2026-08-09"
    if target_db and os.path.exists(target_db):
        try:
            conn = sqlite3.connect(target_db)
            cur = conn.cursor()
            cur.execute("SELECT MAX(order_date) FROM orders;")
            row = cur.fetchone()
            if row and row[0]:
                max_date = str(row[0])[:10]
            conn.close()
        except Exception:
            pass

    # 1. Convert nested DATE_FORMAT(DATE_SUB(...), '%Y-%m') expressions first
    s = re.sub(
        r"DATE_FORMAT\(\s*DATE_SUB\(\s*(CURDATE\(\)|CURRENT_DATE\(\)|CURRENT_DATE)\s*,\s*INTERVAL\s+(\d+)\s+(MONTH|DAY|YEAR)\s*\)\s*,\s*'([^']+)'\s*\)",
        r"strftime('\4', date('" + max_date + r"', '-\2 \3'))",
        s,
        flags=re.IGNORECASE
    )
    s = re.sub(
        r"DATE_FORMAT\(\s*DATE_ADD\(\s*(CURDATE\(\)|CURRENT_DATE\(\)|CURRENT_DATE)\s*,\s*INTERVAL\s+(\d+)\s+(MONTH|DAY|YEAR)\s*\)\s*,\s*'([^']+)'\s*\)",
        r"strftime('\4', date('" + max_date + r"', '+\2 \3'))",
        s,
        flags=re.IGNORECASE
    )

    # 2. Convert standalone DATE_SUB / DATE_ADD
    s = re.sub(
        r"DATE_SUB\(\s*(CURDATE\(\)|CURRENT_DATE\(\)|CURRENT_DATE)\s*,\s*INTERVAL\s+(\d+)\s+(MONTH|DAY|YEAR)\s*\)",
        r"date('" + max_date + r"', '-\2 \3')",
        s,
        flags=re.IGNORECASE
    )
    s = re.sub(
        r"DATE_ADD\(\s*(CURDATE\(\)|CURRENT_DATE\(\)|CURRENT_DATE)\s*,\s*INTERVAL\s+(\d+)\s+(MONTH|DAY|YEAR)\s*\)",
        r"date('" + max_date + r"', '+\2 \3')",
        s,
        flags=re.IGNORECASE
    )

    # 3. Convert DATE_FORMAT(col, fmt) -> strftime(fmt, col)
    s = re.sub(
        r"DATE_FORMAT\(\s*([a-zA-Z0-9_\.]+)\s*,\s*'([^']+)'\s*\)",
        r"strftime('\2', \1)",
        s,
        flags=re.IGNORECASE
    )

    # 4. Replace CURDATE() / CURRENT_DATE / NOW()
    s = re.sub(r"\bCURDATE\(\)", f"'{max_date}'", s, flags=re.IGNORECASE)
    s = re.sub(r"\bCURRENT_DATE\(\)", f"'{max_date}'", s, flags=re.IGNORECASE)
    s = re.sub(r"\bCURRENT_DATE\b", f"'{max_date}'", s, flags=re.IGNORECASE)
    s = re.sub(r"\bNOW\(\)", f"'{max_date}'", s, flags=re.IGNORECASE)

    )

    return s


def generate_smart_followup_suggestions(question: str, results=None, active_mode: str = "mysql") -> list:
    """Generates 3 contextual follow-up question chips based on question intent and active mode."""
    q_lower = question.lower()

    if active_mode == "csv":
        if "revenue" in q_lower or "sales" in q_lower or "price" in q_lower:
            return [
                "Which category generated the highest total revenue?",
                "What is the average transaction value across all orders?",
                "Show monthly sales performance comparison"
            ]
        elif "customer" in q_lower or "user" in q_lower:
            return [
                "Top 5 most frequent purchasing customers",
                "What is the distribution of orders per customer?",
                "Which region has the highest number of active customers?"
            ]
        elif "product" in q_lower or "item" in q_lower:
            return [
                "Top 10 highest-priced items in dataset",
                "Which products have the highest order quantity?",
                "Show breakdown of items by category"
            ]
        else:
            return [
                "What are the top 5 performing items by metric?",
                "Show average and total values across categories",
                "Compare top vs bottom performing entries"
            ]
    else:
        # Default MySQL business_db mode
        if "revenue" in q_lower or "sale" in q_lower or "month" in q_lower:
            return [
                "Which region generated the highest revenue?",
                "Top 5 most profitable products",
                "Compare quarterly sales trends for orders"
            ]
        elif "product" in q_lower or "item" in q_lower or "category" in q_lower:
            return [
                "Which product category has the highest unit sales?",
                "Show top 5 products with highest unit prices",
                "List suppliers providing top selling products"
            ]
        elif "customer" in q_lower or "region" in q_lower:
            return [
                "Which customer placed the most orders?",
                "Show order volume breakdown by region",
                "What is the average order value per customer?"
            ]
        else:
            return [
                "Compair last 2 month revenue",
                "Most sale product in last 1month",
                "Top 5 customers with highest total order spending"
            ]


# ==========================================
# SMART QUERY EXECUTOR
# ==========================================

def smart_execute_query(sql: str, session_id: str = "default_session"):
    """Executes query against selected active dataset for this isolated session (CSV SQLite or MySQL)."""
    db_path = get_session_db_path(session_id)
    active_mode = get_session_active_mode(session_id)
    active_table = get_session_active_table(session_id)

    if active_mode == "csv" and os.path.exists(db_path):
        try:
            exec_sql = sql
            if active_table and active_table != "uploaded_data":
                exec_sql = re.sub(r'\buploaded_data\b', f"`{active_table}`", sql, flags=re.IGNORECASE)

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(exec_sql)
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return "No results found."
            return [dict(r) for r in rows]
        except Exception as e:
            print("SQLite query error, attempting fallback on uploaded_data:", e)
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                conn.close()
                if not rows:
                    return "No results found."
                return [dict(r) for r in rows]
            except Exception as e2:
                print("SQLite fallback error:", e2)

    # Execute against MySQL with cloud default_business.db fallback
    try:
        return execute_query(sql)
    except Exception as mysql_err:
        print("MySQL Connection Notice (using cloud default_business.db fallback):", mysql_err)
        
        possible_paths = [
            "default_business.db",
            "backend/default_business.db",
            os.path.join(os.path.dirname(__file__), "..", "..", "default_business.db"),
            os.path.join(os.path.dirname(__file__), "..", "default_business.db")
        ]
        
        target_db = None
        for p in possible_paths:
            if os.path.exists(p):
                target_db = p
                break
                
        if not target_db:
            try:
                from app.database.default_db_seeder import seed_default_business_db
                seed_default_business_db()
                target_db = "default_business.db"
            except Exception as seed_err:
                print("Seeder error:", seed_err)

        if target_db and os.path.exists(target_db):
            try:
                sqlite_sql = convert_mysql_sql_to_sqlite(sql, target_db)
                conn = sqlite3.connect(target_db)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(sqlite_sql)
                rows = cursor.fetchall()
                conn.close()
                if not rows:
                    return "No results found."
                return [dict(r) for r in rows]
            except Exception as sqlite_err:
                print("Default SQLite fallback execution error:", sqlite_err)

        raise mysql_err


# ==========================================
# ASK ENDPOINT
# ==========================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()
    session_id = request.session_id or "default_session"
    active_mode = get_session_active_mode(session_id)
    active_table = get_session_active_table(session_id)
    active_filename = get_session_active_filename(session_id)
    db_path = get_session_db_path(session_id)

    if not question:
        raise HTTPException(status_code=400, detail="Please provide a valid business question.")

    # 1. DUAL-MODE INTENT ROUTER (Conversational General AI vs Data Query)
    intent_type, gen_ai_answer = classify_intent_and_answer(question)
    if intent_type == "conversational":
        return {
            "success": True,
            "question": question,
            "session_id": session_id,
            "data_source": "🤖 Groq AI Engine",
            "active_mode": active_mode,
            "sql": None,
            "results": [],
            "answer": gen_ai_answer,
            "chart": None
        }

    clarification = get_clarification(question)
    if clarification:
        return {
            "success": True,
            "question": question,
            "clarification": True,
            "sql": None,
            "results": [],
            "answer": clarification.get("message", "Could you please clarify your question?"),
            "suggestions": clarification.get("suggestions", []),
            "chart": None
        }

    try:
        raw_history = get_session_history(session_id)
        
        # Filter history to prevent cross-dataset SQL schema leaks!
        history = []
        for h in raw_history:
            sql_text = h.get("sql", "")
            if active_mode == "mysql":
                if "uploaded_data" not in sql_text and not sql_text.startswith("csv_tbl_") and "tax_revenue" not in sql_text:
                    history.append(h)
            elif active_mode == "csv":
                if active_table in sql_text or "uploaded_data" in sql_text:
                    history.append(h)

        augmented_question = question
        if history:
            history_summary = "\n".join([
                f"Previous Question: {h['question']}\nPrevious SQL: {h['sql']}"
                for h in history if h.get("sql")
            ])
            if history_summary:
                augmented_question = (
                    f"Conversation Context:\n{history_summary}\n\n"
                    f"Current Follow-up Question: {question}"
                )

        try:
            sql = generate_sql(question, history=history, session_id=session_id)
        except TypeError:
            sql = generate_sql(augmented_question, session_id=session_id)

        if not sql:
            raise HTTPException(status_code=500, detail="Failed to generate SQL query for your question.")

        sql = sql.strip().rstrip(";")

        is_safe, message = validate_sql(sql)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"Unsafe SQL query detected: {message}")

        guardrail_safe, guardrail_msg = strict_security_guardrail(sql)
        if not guardrail_safe:
            raise HTTPException(status_code=403, detail=f"Security Policy Error: {guardrail_msg}")

        # Execute query against active mode dataset
        try:
            results = smart_execute_query(sql, session_id=session_id)

            chart = None
            if should_generate_chart(question):
                chart = generate_chart_data(results)

            if not chart and isinstance(results, list) and len(results) >= 2:
                chart = generate_chart_data(results)

            formatted_results = format_results(results)
            answer = generate_business_answer(question, formatted_results)

            save_session_turn(session_id, question, sql, answer)

            if active_mode == "csv" and os.path.exists(db_path):
                data_source = f"📁 CSV: {active_filename or 'Uploaded Dataset'}"
            else:
                data_source = "🗄️ Database: MySQL (business_db)"

            followups = generate_smart_followup_suggestions(question, results, active_mode)
            return {
                "success": True,
                "question": question,
                "session_id": session_id,
                "data_source": data_source,
                "active_mode": active_mode,
                "sql": sql,
                "results": formatted_results,
                "answer": answer,
                "chart": chart,
                "followup_suggestions": followups
            }

        except Exception as query_err:
            print("Database Query Execution Warning:", query_err)
            if active_mode == "mysql":
                answer_msg = (
                    f"### 🗄️ Generated SQL Query for MySQL (business_db):\n```sql\n{sql}\n```\n\n"
                    "📌 **MySQL Database Status**:\n"
                    "The Text-to-SQL engine successfully generated the exact query for your MySQL `business_db` database!\n\n"
                    "• **Local PC Execution**: Run the backend locally (`localhost:8000`) to execute this query directly against your local MySQL server.\n"
                    "• **Cloud Web Demo Execution**: To test live data execution, KPI cards, and charts on this cloud demo, select an uploaded CSV dataset from the top **Active Dataset** dropdown or click **📁 Upload CSV**!"
                )
                save_session_turn(session_id, question, sql, answer_msg)
                return {
                    "success": True,
                    "question": question,
                    "session_id": session_id,
                    "data_source": "🗄️ Database: MySQL (business_db)",
                    "active_mode": active_mode,
                    "sql": sql,
                    "results": [],
                    "answer": answer_msg,
                    "chart": None,
                    "followup_suggestions": generate_smart_followup_suggestions(question, None, active_mode)
                }
            raise

    except HTTPException:
        raise

    except Exception as e:
        print("RUNTIME ERROR IN /ask:", str(e))
        if ACTIVE_DATASET_MODE == "csv" and os.path.exists(CSV_DB_PATH):
            data_source = f"📁 CSV: {ACTIVE_CSV_FILENAME or 'Uploaded Dataset'}"
        else:
            data_source = "🗄️ Database: MySQL (business_db)"

        return {
            "success": True,
            "question": question,
            "session_id": session_id,
            "data_source": data_source,
            "active_mode": ACTIVE_DATASET_MODE,
            "sql": None,
            "results": [],
            "answer": (
                "Hello! 👋 I am your AI Business Intelligence Assistant. "
                "I specialize in analyzing data across your active datasets (sales, orders, revenue, products, customers, or uploaded CSV metrics). "
                "Your question appears to be outside the scope of the active dataset. Please try asking a data or business-related question!"
            ),
            "chart": None
        }