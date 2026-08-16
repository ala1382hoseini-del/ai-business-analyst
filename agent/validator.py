"""
validator.py
-------------
Safety layer between the LLM's generated SQL and the database.
Never trust generated SQL -- always validate before execution.
"""

import re

BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
    "VACUUM", "REINDEX", "GRANT", "REVOKE",
]


class SQLValidationError(Exception):
    pass


def validate_sql(sql: str) -> None:
    """Raise SQLValidationError if the query is anything other than a
    single, safe SELECT statement. Returns None (i.e. passes silently)
    if the query is safe."""

    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL query.")

    stripped = sql.strip()

    # Must start with SELECT (allow leading whitespace/newlines only)
    if not re.match(r"^\s*SELECT\b", stripped, re.IGNORECASE):
        raise SQLValidationError(
            "Only SELECT statements are allowed. Query must start with SELECT."
        )

    # Block multiple statements (e.g. "SELECT ...; DROP TABLE ...")
    # A single trailing semicolon is fine; anything after it is not.
    body = stripped.rstrip(";").strip()
    if ";" in body:
        raise SQLValidationError(
            "Multiple SQL statements are not allowed."
        )

    # Block dangerous keywords anywhere in the query (as whole words, so
    # e.g. a product name containing "update" in text wouldn't false-positive
    # -- though realistically this only matters for the query structure)
    for keyword in BLOCKED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", body, re.IGNORECASE):
            raise SQLValidationError(
                f"Query contains a disallowed keyword: {keyword}"
            )


def is_safe(sql: str) -> bool:
    try:
        validate_sql(sql)
        return True
    except SQLValidationError:
        return False


if __name__ == "__main__":
    tests = [
        "SELECT * FROM sales LIMIT 5",
        "DROP TABLE sales",
        "SELECT * FROM sales; DROP TABLE sales;",
        "UPDATE sales SET sales = 0",
        "SELECT region, SUM(sales) FROM sales GROUP BY region",
    ]
    for t in tests:
        try:
            validate_sql(t)
            print(f"OK   : {t}")
        except SQLValidationError as e:
            print(f"BLOCK: {t}  -->  {e}")
