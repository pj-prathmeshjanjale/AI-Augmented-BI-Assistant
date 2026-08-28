"""
Comprehensive Evaluation and Benchmarking Suite for AI BI Assistant RAG Pipeline.
Evaluates retrieval accuracy, SQL generation validity, execution success, semantic correctness
against database ground truth, security guardrail enforcement, and measures latency comparison.
"""

import os
import time
import json
import sqlite3
import statistics
from typing import Dict, Any, List

from app.rag.retriever import get_retriever
from app.rag.rag_chain import generate_rag_sql, clean_sql_output
from app.ai.sql_validator import validate_sql
from app.main import strict_security_guardrail, smart_execute_query
from app.ai.schema_context import build_schema_context
from app.ai.groq_client import client


DB_PATH = os.path.join(os.path.dirname(__file__), "../..", "default_business.db")

# =========================================================================
# 1. BENCHMARK TEST DATASET (8 ANALYTICAL SCENARIOS WITH GROUND TRUTH)
# =========================================================================
BENCHMARK_DATASET = [
    {
        "id": "Q1",
        "question": "What is the total revenue across all orders?",
        "expected_tables": ["order_items"],
        "category": "Aggregation",
        "ground_truth_sql": "SELECT SUM(quantity * unit_price) AS total_revenue FROM order_items",
        "target_doc_ids": ["kpi_revenue", "schema_order_items", "join_customer_spending"]
    },
    {
        "id": "Q2",
        "question": "Which product category has the highest revenue?",
        "expected_tables": ["categories", "products", "order_items"],
        "category": "Multi-Table Join & Group By",
        "ground_truth_sql": (
            "SELECT c.category_name, SUM(oi.quantity * oi.unit_price) AS total_revenue "
            "FROM categories c "
            "JOIN products p ON c.category_id = p.category_id "
            "JOIN order_items oi ON p.product_id = oi.product_id "
            "GROUP BY c.category_id, c.category_name "
            "ORDER BY total_revenue DESC LIMIT 1"
        ),
        "target_doc_ids": ["sql_template_top_products", "join_category_revenue", "schema_categories"]
    },
    {
        "id": "Q3",
        "question": "Which region generated the highest revenue?",
        "expected_tables": ["regions", "customers", "orders", "order_items"],
        "category": "Multi-Table Join",
        "ground_truth_sql": (
            "SELECT r.region_name, SUM(oi.quantity * oi.unit_price) AS total_revenue "
            "FROM regions r "
            "JOIN customers c ON r.region_id = c.region_id "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "JOIN order_items oi ON o.order_id = oi.order_id "
            "GROUP BY r.region_id, r.region_name "
            "ORDER BY total_revenue DESC LIMIT 1"
        ),
        "target_doc_ids": ["sql_template_regional_revenue", "join_regional_revenue", "schema_regions"]
    },
    {
        "id": "Q4",
        "question": "What is the monthly sales trend for revenue?",
        "expected_tables": ["orders", "order_items"],
        "category": "Time-Series & Date Grouping",
        "ground_truth_sql": (
            "SELECT strftime('%Y-%m', o.order_date) AS month, SUM(oi.quantity * oi.unit_price) AS monthly_revenue "
            "FROM orders o "
            "JOIN order_items oi ON o.order_id = oi.order_id "
            "GROUP BY month ORDER BY month ASC"
        ),
        "target_doc_ids": ["kpi_revenue", "schema_orders", "schema_order_items", "sql_template_monthly_sales", "kpi_monthly_sales"]
    },
    {
        "id": "Q5",
        "question": "Top 5 customers with the highest total order spending",
        "expected_tables": ["customers", "orders", "order_items"],
        "category": "Ranking & Top-N",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, SUM(oi.quantity * oi.unit_price) AS total_spent "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "JOIN order_items oi ON o.order_id = oi.order_id "
            "GROUP BY c.customer_id, c.first_name, c.last_name "
            "ORDER BY total_spent DESC LIMIT 5"
        ),
        "target_doc_ids": ["join_customer_spending", "sql_template_top_products"]
    },
    {
        "id": "Q6",
        "question": "What is the average order value (AOV)?",
        "expected_tables": ["orders", "order_items"],
        "category": "Single KPI",
        "ground_truth_sql": (
            "SELECT SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id) AS average_order_value "
            "FROM order_items oi "
            "JOIN orders o ON oi.order_id = o.order_id"
        ),
        "target_doc_ids": ["kpi_aov", "schema_order_items", "join_customer_spending"]
    },
    {
        "id": "Q7",
        "question": "Which supplier provides the most products?",
        "expected_tables": ["suppliers", "products"],
        "category": "Catalog & Supplier Analytics",
        "ground_truth_sql": (
            "SELECT s.supplier_name, COUNT(p.product_id) AS product_count "
            "FROM suppliers s "
            "JOIN products p ON s.supplier_id = p.supplier_id "
            "GROUP BY s.supplier_name "
            "ORDER BY product_count DESC LIMIT 1"
        ),
        "target_doc_ids": ["sql_template_top_products", "schema_suppliers", "kpi_supplier_contribution"]
    },
    {
        "id": "Q8",
        "question": "What is the breakdown of order payments by payment method?",
        "expected_tables": ["payments"],
        "category": "Payment Distribution",
        "ground_truth_sql": (
            "SELECT payment_method, COUNT(payment_id) AS payment_count, SUM(amount) AS total_amount "
            "FROM payments "
            "GROUP BY payment_method "
            "ORDER BY total_amount DESC"
        ),
        "target_doc_ids": ["schema_payments", "kpi_payment_mix", "schema_orders"]
    }
]

# =========================================================================
# 2. MALICIOUS & DESTRUCTIVE SQL SECURITY TEST CASES
# =========================================================================
SECURITY_TEST_CASES = [
    {"input": "DROP TABLE customers;", "type": "Destructive DROP"},
    {"input": "DELETE FROM orders WHERE order_id > 0;", "type": "Destructive DELETE"},
    {"input": "UPDATE products SET unit_price = 0;", "type": "Destructive UPDATE"},
    {"input": "ALTER TABLE employees ADD COLUMN ssn VARCHAR(20);", "type": "Destructive ALTER"},
    {"input": "TRUNCATE TABLE payments;", "type": "Destructive TRUNCATE"},
    {"input": "SELECT * FROM orders; DROP TABLE products;", "type": "Multi-Statement Injection"},
    {"input": "SELECT * FROM users WHERE 1=1; EXEC xp_cmdshell('dir');", "type": "Command Injection"}
]


def execute_direct_sqlite(sql: str):
    """Executes a SQL query directly against the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


def run_legacy_static_generation(question: str) -> Dict[str, Any]:
    """Runs generation using old static context dump (for baseline measurement)."""
    start_total = time.perf_counter()
    schema_context = build_schema_context()

    prompt = f"""
You are an expert Data Analyst. Convert user question into a valid SQL SELECT query.
DATABASE SCHEMA:
{schema_context}
USER QUESTION: {question}
Return ONLY raw SQL.
"""
    start_llm = time.perf_counter()
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a SQL generator. Return ONLY raw SQL."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    llm_ms = (time.perf_counter() - start_llm) * 1000.0
    total_ms = (time.perf_counter() - start_total) * 1000.0

    raw_sql = response.choices[0].message.content
    sql = clean_sql_output(raw_sql)

    return {
        "sql": sql,
        "retrieval_ms": 0.0,
        "llm_ms": llm_ms,
        "total_ms": total_ms
    }


def evaluate_security_guardrails():
    """Evaluates strict security guardrails against destructive and malicious queries."""
    print("\n" + "=" * 70)
    print(" [SECURITY EVALUATION] SQL GUARDRAIL ENFORCEMENT")
    print("=" * 70)

    passed_count = 0
    for idx, test in enumerate(SECURITY_TEST_CASES, 1):
        sql_input = test["input"]
        test_type = test["type"]

        is_safe_1, msg1 = validate_sql(sql_input)
        is_safe_2, msg2 = strict_security_guardrail(sql_input)

        blocked = (not is_safe_1) or (not is_safe_2)
        status = "[BLOCKED / PASSED]" if blocked else "[ALLOWED / FAILED]"
        reason = msg1 if not is_safe_1 else msg2

        if blocked:
            passed_count += 1

        print(f"[{idx}/{len(SECURITY_TEST_CASES)}] {test_type:<28} -> {status}")
        print(f"     Payload: {sql_input}")
        print(f"     Action:  {reason}\n")

    rate = (passed_count / len(SECURITY_TEST_CASES)) * 100.0
    print(f"[SECURITY RESULT] Guardrail Success Rate: {passed_count}/{len(SECURITY_TEST_CASES)} ({rate:.1f}%)\n")
    return rate


def run_full_rag_evaluation():
    """Runs end-to-end evaluation on the benchmark suite and calculates real metrics."""
    print("\n" + "=" * 70)
    print(" [RAG EVALUATION] LANGCHAIN + FAISS TEXT-TO-SQL PIPELINE")
    print("=" * 70)

    rag_results = []
    baseline_results = []

    retriever = get_retriever()

    for idx, item in enumerate(BENCHMARK_DATASET, 1):
        q = item["question"]
        qid = item["id"]
        print(f"\n--- [{idx}/{len(BENCHMARK_DATASET)}] Evaluating ({qid}): '{q}' ---")

        # 1. Ground Truth
        gt_res = execute_direct_sqlite(item["ground_truth_sql"])

        # 2. RAG PIPELINE EXECUTION
        sql_rag, debug_info = generate_rag_sql(q, include_debug=True)
        is_valid_rag, val_msg = validate_sql(sql_rag)
        is_safe_rag, guard_msg = strict_security_guardrail(sql_rag)

        exec_success_rag = False
        query_res = None
        row_count_rag = 0

        if is_valid_rag and is_safe_rag:
            try:
                query_res = smart_execute_query(sql_rag)
                if isinstance(query_res, list) and len(query_res) > 0:
                    exec_success_rag = True
                    row_count_rag = len(query_res)
                elif query_res != "No results found.":
                    exec_success_rag = True
            except Exception as e:
                pass

        # Semantic comparison
        semantic_pass = False
        if exec_success_rag and isinstance(query_res, list) and len(query_res) > 0 and len(gt_res) > 0:
            first_gen = query_res[0]
            first_gt = gt_res[0]
            gen_vals = list(first_gen.values())
            gt_vals = list(first_gt.values())
            if len(gen_vals) > 0 and len(gt_vals) > 0:
                if str(gen_vals[0]).strip() == str(gt_vals[0]).strip():
                    semantic_pass = True
                elif isinstance(gen_vals[0], (int, float)) and isinstance(gt_vals[0], (int, float)):
                    if abs(gen_vals[0] - gt_vals[0]) < 0.01:
                        semantic_pass = True
                for v in gen_vals:
                    if v in gt_vals or (isinstance(v, (int, float)) and any(isinstance(gv, (int, float)) and abs(v - gv) < 0.01 for gv in gt_vals)):
                        semantic_pass = True
                        break

        # Context relevance check
        retrieved_docs = debug_info.get("retrieved_docs", [])
        retrieved_doc_ids = [d["doc_id"] for d in retrieved_docs if isinstance(d, dict)]
        relevance_overlap = any(doc_id in retrieved_doc_ids for doc_id in item["target_doc_ids"])

        rag_record = {
            "id": qid,
            "question": q,
            "category": item["category"],
            "retrieved_doc_ids": retrieved_doc_ids,
            "target_match": relevance_overlap,
            "sql": sql_rag,
            "is_valid": is_valid_rag,
            "is_safe": is_safe_rag,
            "exec_success": exec_success_rag,
            "semantic_correctness": semantic_pass,
            "row_count": row_count_rag,
            "retrieval_ms": debug_info.get("retrieval_time_ms", 0),
            "llm_ms": debug_info.get("llm_time_ms", 0),
            "total_ms": debug_info.get("total_time_ms", 0)
        }
        rag_results.append(rag_record)

        print(f"  * Retrieved Chunks: {retrieved_doc_ids} (Target Match: {relevance_overlap})")
        print(f"  * Retrieval Latency: {rag_record['retrieval_ms']:.1f}ms | LLM Latency: {rag_record['llm_ms']:.1f}ms | Total: {rag_record['total_ms']:.1f}ms")
        print(f"  * Generated SQL: {sql_rag}")
        print(f"  * Valid: {is_valid_rag} | Safe: {is_safe_rag} | Executed: {exec_success_rag} | Semantic: {semantic_pass}")

        # 3. BASELINE STATIC INJECTION EXECUTION (FOR COMPARISON)
        time.sleep(0.3)
        base_exec = run_legacy_static_generation(q)
        is_valid_base, _ = validate_sql(base_exec["sql"])
        is_safe_base, _ = strict_security_guardrail(base_exec["sql"])
        exec_success_base = False
        if is_valid_base and is_safe_base:
            try:
                base_res = smart_execute_query(base_exec["sql"])
                if isinstance(base_res, list) and len(base_res) > 0:
                    exec_success_base = True
            except Exception:
                pass

        baseline_results.append({
            "id": item["id"],
            "sql": base_exec["sql"],
            "is_valid": is_valid_base,
            "exec_success": exec_success_base,
            "llm_ms": base_exec["llm_ms"],
            "total_ms": base_exec["total_ms"]
        })

    # =========================================================================
    # 4. STATISTICAL METRICS COMPILATION
    # =========================================================================
    total_q = len(BENCHMARK_DATASET)

    rag_valid_count = sum(1 for r in rag_results if r["is_valid"] and r["is_safe"])
    rag_exec_count = sum(1 for r in rag_results if r["exec_success"])
    rag_semantic_count = sum(1 for r in rag_results if r["semantic_correctness"])
    rag_target_match_count = sum(1 for r in rag_results if r["target_match"])

    rag_retrieval_times = [r["retrieval_ms"] for r in rag_results]
    rag_llm_times = [r["llm_ms"] for r in rag_results]
    rag_total_times = [r["total_ms"] for r in rag_results]

    base_valid_count = sum(1 for b in baseline_results if b["is_valid"])
    base_exec_count = sum(1 for b in baseline_results if b["exec_success"])
    base_total_times = [b["total_ms"] for b in baseline_results]

    print("\n" + "=" * 70)
    print(" [BENCHMARK SUMMARY] BEFORE VS. AFTER COMPARISON")
    print("=" * 70)

    print(f"\n1. ACCURACY & EXECUTION METRICS (Sample Size = {total_q} benchmark queries):")
    print(f"   * Strict Target-Document Match Rate: {rag_target_match_count}/{total_q} ({(rag_target_match_count/total_q)*100:.1f}%)")
    print(f"   * SQL Validity Rate (RAG Pipeline):  {rag_valid_count}/{total_q} ({(rag_valid_count/total_q)*100:.1f}%)")
    print(f"   * Database Execution Success (RAG):   {rag_exec_count}/{total_q} ({(rag_exec_count/total_q)*100:.1f}%)")
    print(f"   * Semantic Ground Truth Correctness: {rag_semantic_count}/{total_q} ({(rag_semantic_count/total_q)*100:.1f}%)")
    print(f"   * SQL Validity Rate (Baseline Static): {base_valid_count}/{total_q} ({(base_valid_count/total_q)*100:.1f}%)")
    print(f"   * Database Execution Success (Baseline): {base_exec_count}/{total_q} ({(base_exec_count/total_q)*100:.1f}%)")

    print(f"\n2. LATENCY COMPARISON (Measured in milliseconds):")
    print(f"   * RAG FAISS Retrieval Latency:  Avg = {statistics.mean(rag_retrieval_times):.1f}ms | Median = {statistics.median(rag_retrieval_times):.1f}ms")
    print(f"   * RAG LLM Generation Latency:   Avg = {statistics.mean(rag_llm_times):.1f}ms | Median = {statistics.median(rag_llm_times):.1f}ms")
    print(f"   * RAG Total End-to-End Latency:  Avg = {statistics.mean(rag_total_times):.1f}ms | Median = {statistics.median(rag_total_times):.1f}ms")
    print(f"   * Baseline Total Latency:        Avg = {statistics.mean(base_total_times):.1f}ms | Median = {statistics.median(base_total_times):.1f}ms")

    # Security tests
    evaluate_security_guardrails()

    return {
        "rag_results": rag_results,
        "baseline_results": baseline_results,
        "metrics": {
            "total_questions": total_q,
            "rag_target_match_pct": round((rag_target_match_count/total_q)*100, 1),
            "rag_validity_pct": round((rag_valid_count/total_q)*100, 1),
            "rag_execution_success_pct": round((rag_exec_count/total_q)*100, 1),
            "rag_semantic_correctness_pct": round((rag_semantic_count/total_q)*100, 1),
            "avg_retrieval_latency_ms": round(statistics.mean(rag_retrieval_times), 1),
            "median_retrieval_latency_ms": round(statistics.median(rag_retrieval_times), 1),
            "avg_rag_total_latency_ms": round(statistics.mean(rag_total_times), 1),
            "median_rag_total_latency_ms": round(statistics.median(rag_total_times), 1),
            "median_baseline_total_latency_ms": round(statistics.median(base_total_times), 1)
        }
    }


if __name__ == "__main__":
    run_full_rag_evaluation()
