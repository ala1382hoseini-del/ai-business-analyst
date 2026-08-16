"""
schema.py
----------
LLM-friendly description of the IT Support Ticketing schema (9 related
tables). Unlike a single flat table, this schema requires the model to
know which columns join to which -- so every foreign key relationship
is spelled out explicitly.
"""

import sqlite3
from database.db_setup import DB_PATH

SCHEMA_TEXT = """
This is a customer support ticketing system for an HR/payroll software
company. It has 9 related tables (Persian/Farsi text values are common
in the data -- customer names, product names, ticket subjects, etc).

Table: customers
  - customer_id (TEXT, PK)
  - customer_name (TEXT)
  - industry (TEXT)
  - province (TEXT)
  - city (TEXT)
  - register_date (TEXT, YYYY-MM-DD): when the customer signed up

Table: products
  - product_id (TEXT, PK)
  - product_category_id (TEXT, FK -> product_categories.product_category_id)
  - product_name (TEXT)

Table: product_categories
  - product_category_id (TEXT, PK)
  - product_category_name (TEXT)

Table: support_agents
  - agent_id (TEXT, PK)
  - full_name (TEXT)
  - hire_date (TEXT, YYYY-MM-DD)

Table: tickets  (the central fact table -- one row per support ticket)
  - ticket_id (TEXT, PK)
  - customer_id (TEXT, FK -> customers.customer_id): who filed the ticket
  - product_id (TEXT, FK -> products.product_id): which product it's about
  - agent_id (TEXT, FK -> support_agents.agent_id, NULLABLE): who handled it
    (NULL means unassigned)
  - priority_id (TEXT, FK -> ticket_priorities.priority_id)
  - severity_id (TEXT, FK -> ticket_severities.severity_id)
  - status_id (TEXT, FK -> ticket_statuses.status_id)
  - category_id (TEXT, FK -> ticket_categories.category_id)
  - subject (TEXT): short description of the issue
  - create_date (TEXT, YYYY-MM-DD HH:MM:SS): when the ticket was opened
  - assigned_date (TEXT, YYYY-MM-DD HH:MM:SS, NULLABLE)
  - first_response_date (TEXT, YYYY-MM-DD HH:MM:SS, NULLABLE)
  - close_date (TEXT, YYYY-MM-DD HH:MM:SS, NULLABLE): NULL means still open

Table: ticket_priorities
  - priority_id (TEXT, PK)
  - priority_name (TEXT): 'Low', 'Medium', 'High', 'Critical'

Table: ticket_severities
  - severity_id (TEXT, PK)
  - severity_name (TEXT): 'Low', 'Medium', 'High', 'Critical'

Table: ticket_statuses
  - status_id (TEXT, PK)
  - status_name (TEXT): 'New', 'Assigned', 'In Progress', 'Pending Customer',
    'Resolved', 'Closed', 'Cancelled'

Table: ticket_categories
  - category_id (TEXT, PK)
  - category_name (TEXT): e.g. 'خطای نرم افزار' (software bug),
    'سوال' (question), 'آموزش' (training request), etc.

Common JOIN patterns:
  - Ticket + who filed it: tickets.customer_id = customers.customer_id
  - Ticket + which product: tickets.product_id = products.product_id
  - Ticket + which agent handled it: tickets.agent_id = support_agents.agent_id
  - Ticket + priority/severity/status/category: join the respective
    lookup table on its *_id column to get the human-readable name
    (e.g. join ticket_statuses to show 'Closed' instead of a raw ID)
  - Product + its category: products.product_category_id =
    product_categories.product_category_id

Useful derived metrics:
  - Resolution time = julianday(close_date) - julianday(create_date), in
    days (only meaningful where close_date IS NOT NULL)
  - First response time = julianday(first_response_date) - julianday(create_date)
  - An "open" ticket is one where close_date IS NULL
""".strip()


def get_schema_text() -> str:
    return SCHEMA_TEXT


def verify_schema_matches_db(db_path: str = DB_PATH) -> bool:
    """Sanity check: confirm every table mentioned in the schema text
    actually exists in the database (catches drift after future changes)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    real_tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    documented_tables = {
        line.split("Table:")[1].split("(")[0].strip()
        for line in SCHEMA_TEXT.splitlines()
        if line.strip().startswith("Table:")
    }

    missing = documented_tables - real_tables
    if missing:
        print(f"Schema mismatch! Documented but missing from DB: {missing}")
        return False
    return True


if __name__ == "__main__":
    print(get_schema_text())
    print()
    print("Schema matches DB:", verify_schema_matches_db())
