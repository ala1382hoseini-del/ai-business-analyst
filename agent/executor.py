"""
executor.py
------------
Runs SQL against the SQLite database and orchestrates the full
generate -> validate -> execute -> (retry on error) loop.
"""

import sqlite3
import pandas as pd

from database.db_setup import DB_PATH
from agent.sql_generator import generate_sql
from agent.validator import validate_sql, SQLValidationError

MAX_RETRIES = 2


def run_query(sql: str) -> pd.DataFrame:
    """Execute a validated SELECT query and return results as a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()
    return df


def answer_question(question: str) -> dict:
    """
    Full pipeline for one user question:
      1. Ask the model for SQL
      2. Validate it (safety)
      3. Execute it
      4. If it fails (validation OR execution), feed the error back to the
         model and retry, up to MAX_RETRIES times.

    Returns a dict describing the outcome -- always, never raises, so the
    UI layer can handle every case (success, cannot-answer, failure)
    uniformly.
    """
    last_error = None
    sql = None

    for attempt in range(MAX_RETRIES + 1):
        sql = generate_sql(question, error_feedback=last_error)

        if sql.strip() == "CANNOT_ANSWER":
            return {
                "status": "cannot_answer",
                "question": question,
                "sql": None,
                "data": None,
                "attempts": attempt + 1,
            }

        try:
            validate_sql(sql)
            df = run_query(sql)
            return {
                "status": "success",
                "question": question,
                "sql": sql,
                "data": df,
                "attempts": attempt + 1,
            }
        except SQLValidationError as e:
            last_error = f"Validation error: {e}"
        except sqlite3.Error as e:
            last_error = f"SQLite execution error: {e}"

    return {
        "status": "failed",
        "question": question,
        "sql": sql,
        "data": None,
        "error": last_error,
        "attempts": MAX_RETRIES + 1,
    }


if __name__ == "__main__":
    result = answer_question("What were the total sales in the West region?")
    print(result)
