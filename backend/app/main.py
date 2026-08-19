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
# MULTI-CSV LIBRARY MANAGER STATE
# ==========================================

CSV_DB_PATH = "uploaded_dataset.db"
ACTIVE_DATASET_MODE = "csv" if os.path.exists(CSV_DB_PATH) else "mysql"
ACTIVE_CSV_TABLE = "uploaded_data"
ACTIVE_CSV_FILENAME = "DF_final_feature.csv" if os.path.exists(CSV_DB_PATH) else None


def init_csv_registry():
    if not os.path.exists(CSV_DB_PATH):
        return
    try:
        conn = sqlite3.connect(CSV_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS csv_registry (
                id TEXT PRIMARY KEY,
                filename TEXT,
                table_name TEXT,
                rows INTEGER,
                cols INTEGER
            );
        """)
        if ACTIVE_CSV_FILENAME:
            cursor.execute("INSERT OR IGNORE INTO csv_registry VALUES (?, ?, ?, ?, ?)",
                           ("csv_uploaded_data", ACTIVE_CSV_FILENAME, "uploaded_data", 202616, 22))
        conn.commit()
        conn.close()
    except Exception as e:
        print("CSV Registry initialization notice:", e)

init_csv_registry()


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
def health_check():
    return {
        "status": "healthy",
        "active_mode": ACTIVE_DATASET_MODE,
        "active_table": ACTIVE_CSV_TABLE,
        "csv_dataset_available": os.path.exists(CSV_DB_PATH),
        "active_csv_filename": ACTIVE_CSV_FILENAME,
        "conversational_memory": "active",
        "active_sessions": len(SESSION_HISTORY)
    }


@app.get("/datasets")
def list_datasets():
    """Returns all available datasets (MySQL + all saved CSV library datasets)."""
    datasets = [
        {"id": "mysql", "name": "🗄️ Default MySQL Database (business_db)", "active": ACTIVE_DATASET_MODE == "mysql"}
    ]
    if os.path.exists(CSV_DB_PATH):
        try:
            conn = sqlite3.connect(CSV_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS csv_registry (id TEXT PRIMARY KEY, filename TEXT, table_name TEXT, rows INTEGER, cols INTEGER);")
            cursor.execute("SELECT id, filename, table_name FROM csv_registry")
            records = cursor.fetchall()
            conn.close()

            if not records:
                datasets.append({
                    "id": "csv:uploaded_data",
                    "name": f"📁 CSV: {ACTIVE_CSV_FILENAME or 'Uploaded Dataset'}",
                    "active": (ACTIVE_DATASET_MODE == "csv")
                })
            else:
                for csv_id, fname, tbl_name in records:
                    is_active = (ACTIVE_DATASET_MODE == "csv" and ACTIVE_CSV_TABLE == tbl_name)
                    datasets.append({
                        "id": f"csv:{tbl_name}",
                        "name": f"📁 CSV: {fname}",
                        "active": is_active
                    })
        except Exception as e:
            print("Error listing CSV library datasets:", e)
            datasets.append({
                "id": "csv:uploaded_data",
                "name": f"📁 CSV: {ACTIVE_CSV_FILENAME or 'Uploaded Dataset'}",
                "active": (ACTIVE_DATASET_MODE == "csv")
            })

    return {
        "active_mode": ACTIVE_DATASET_MODE,
        "active_table": ACTIVE_CSV_TABLE,
        "datasets": datasets
    }


@app.post("/switch_dataset")
def switch_dataset(request: SwitchDatasetRequest):
    """Switch active query engine between MySQL and any saved CSV table."""
    global ACTIVE_DATASET_MODE, ACTIVE_CSV_TABLE, ACTIVE_CSV_FILENAME
    target_mode = request.mode.strip()

    if target_mode.startswith("csv"):
        if not os.path.exists(CSV_DB_PATH):
            raise HTTPException(status_code=400, detail="No CSV dataset available. Please upload a CSV first.")
        
        parts = target_mode.split(":", 1)
        tbl_name = parts[1] if len(parts) > 1 else "uploaded_data"

        conn = sqlite3.connect(CSV_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS csv_registry (id TEXT PRIMARY KEY, filename TEXT, table_name TEXT, rows INTEGER, cols INTEGER);")
        cursor.execute("SELECT filename FROM csv_registry WHERE table_name = ?", (tbl_name,))
        row = cursor.fetchone()
        conn.close()

        ACTIVE_DATASET_MODE = "csv"
        ACTIVE_CSV_TABLE = tbl_name
        if row:
            ACTIVE_CSV_FILENAME = row[0]

        label = ACTIVE_CSV_FILENAME or tbl_name
        return {
            "success": True,
            "active_mode": "csv",
            "active_table": ACTIVE_CSV_TABLE,
            "message": f"Switched active dataset to CSV: {label}"
        }

    elif target_mode == "mysql":
        ACTIVE_DATASET_MODE = "mysql"
        return {
            "success": True,
            "active_mode": "mysql",
            "message": "Switched active dataset to MySQL Database (business_db)"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid dataset mode selection.")


@app.api_route("/delete_dataset/{dataset_id:path}", methods=["DELETE", "POST", "OPTIONS"])
def delete_dataset(dataset_id: str):
    """Deletes an uploaded CSV dataset table from library and resets active mode if needed."""
    global ACTIVE_DATASET_MODE, ACTIVE_CSV_TABLE, ACTIVE_CSV_FILENAME

    if dataset_id == "mysql":
        raise HTTPException(status_code=400, detail="Cannot delete default MySQL system database.")

    tbl_name = dataset_id.replace("csv:", "").strip()

    if not os.path.exists(CSV_DB_PATH):
        raise HTTPException(status_code=404, detail="No CSV library found.")

    try:
        conn = sqlite3.connect(CSV_DB_PATH)
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

        if ACTIVE_CSV_TABLE == tbl_name or ACTIVE_DATASET_MODE == "csv":
            if remaining:
                ACTIVE_DATASET_MODE = "csv"
                ACTIVE_CSV_TABLE = remaining[0][2]
                ACTIVE_CSV_FILENAME = remaining[0][1]
            else:
                ACTIVE_DATASET_MODE = "mysql"
                ACTIVE_CSV_TABLE = "uploaded_data"
                ACTIVE_CSV_FILENAME = None

        return {
            "success": True,
            "message": f"Successfully deleted dataset '{deleted_filename}' from library.",
            "active_mode": ACTIVE_DATASET_MODE
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
def get_csv_health():
    """Generates health inspection stats for active SQLite CSV dataset."""
    if not os.path.exists(CSV_DB_PATH):
        raise HTTPException(status_code=400, detail="No active CSV dataset found.")

    try:
        conn = sqlite3.connect(CSV_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info(`{ACTIVE_CSV_TABLE}`);")
        cols_info = cursor.fetchall()
        if not cols_info:
            cursor.execute("PRAGMA table_info(`uploaded_data`);")
            cols_info = cursor.fetchall()

        clean_headers = [c[1] for c in cols_info]

        cursor.execute(f"SELECT * FROM `{ACTIVE_CSV_TABLE}` LIMIT 3000;")
        sample_rows = [list(r) for r in cursor.fetchall()]

        cursor.execute(f"SELECT COUNT(*) FROM `{ACTIVE_CSV_TABLE}`;")
        total_count = cursor.fetchone()[0]
        conn.close()

        health_report = inspect_dataset_health(sample_rows, clean_headers, total_rows=total_count)
        health_report["filename"] = ACTIVE_CSV_FILENAME or "uploaded_dataset.csv"
        return health_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inspect CSV health: {str(e)}")


# ==========================================
# CSV UPLOAD & MULTI-LIBRARY INGESTION ENDPOINT
# ==========================================

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    global ACTIVE_DATASET_MODE, ACTIVE_CSV_FILENAME, ACTIVE_CSV_TABLE
    
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    try:
        clean_tbl_name = "csv_tbl_" + re.sub(r'\W+', '_', file.filename.strip().lower()).strip('_')
        ACTIVE_CSV_FILENAME = file.filename
        ACTIVE_CSV_TABLE = clean_tbl_name
        ACTIVE_DATASET_MODE = "csv"

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

        conn = sqlite3.connect(CSV_DB_PATH)
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


# ==========================================
# SMART QUERY EXECUTOR
# ==========================================

def smart_execute_query(sql: str):
    """Executes query against selected active dataset (CSV SQLite or MySQL)."""
    if ACTIVE_DATASET_MODE == "csv" and os.path.exists(CSV_DB_PATH):
        try:
            exec_sql = sql
            if ACTIVE_CSV_TABLE and ACTIVE_CSV_TABLE != "uploaded_data":
                exec_sql = re.sub(r'\buploaded_data\b', f"`{ACTIVE_CSV_TABLE}`", sql, flags=re.IGNORECASE)

            conn = sqlite3.connect(CSV_DB_PATH)
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
                conn = sqlite3.connect(CSV_DB_PATH)
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

    # Execute against MySQL
    return execute_query(sql)


# ==========================================
# ASK ENDPOINT
# ==========================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()
    session_id = request.session_id or "default_session"

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
            "active_mode": ACTIVE_DATASET_MODE,
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
        history = get_session_history(session_id)
        
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
            sql = generate_sql(question, history=history)
        except TypeError:
            sql = generate_sql(augmented_question)

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
        results = smart_execute_query(sql)

        chart = None
        if should_generate_chart(question):
            chart = generate_chart_data(results)

        if not chart and isinstance(results, list) and len(results) >= 2:
            chart = generate_chart_data(results)

        formatted_results = format_results(results)
        answer = generate_business_answer(question, formatted_results)

        save_session_turn(session_id, question, sql, answer)

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
            "sql": sql,
            "results": formatted_results,
            "answer": answer,
            "chart": chart
        }

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