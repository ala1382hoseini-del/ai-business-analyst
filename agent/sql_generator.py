"""
sql_generator.py
------------------
Turns a natural-language question into a SQLite SELECT query using
Gemini. This is the "prompt engineering" core of the agent: the quality
of this one prompt drives the quality of the whole product.
"""

from google import genai
from utils.config import GEMINI_API_KEY, GEMINI_MODEL
from database.schema import get_schema_text

_client = genai.Client(api_key=GEMINI_API_KEY)

SQL_SYSTEM_PROMPT = """You are a SQLite expert that converts a business user's
question into a single valid SQLite SELECT query.

{schema}

Rules (follow all of them exactly):
1. Output ONLY the SQL query. No explanation, no markdown code fences, no
   comments, no leading/trailing text.
2. Only ever write a SELECT statement. Never write INSERT, UPDATE, DELETE,
   DROP, ALTER, CREATE, or any other statement type.
3. Only use tables and columns that appear in the schema above. Never invent
   a column or table name.
4. If the question cannot be answered with the available schema (e.g. it
   asks about profit, discount, or quantity, which do not exist), output
   exactly: CANNOT_ANSWER
5. If the question is ambiguous, make the most reasonable assumption a
   business analyst would make, rather than asking for clarification.
6. Prefer clear, simple SQL. Use meaningful column aliases for computed
   values (e.g. SUM(sales) AS total_sales).
7. Always add a reasonable LIMIT (e.g. LIMIT 50) to queries that could
   return many rows, unless the user clearly wants an aggregate (a single
   summary row).
"""


def _clean_sql(raw_text: str) -> str:
    """Strip markdown fences etc. in case the model adds them despite
    instructions -- defensive cleanup, not a substitute for validation."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("sql"):
            text = text[3:]
    return text.strip().rstrip(";").strip()


def generate_sql(question: str, error_feedback: str = None) -> str:
    """
    Generate a SQL query for the given natural language question.

    If error_feedback is provided, it's a previous SQL error message --
    used on retries so the model can fix its own mistake.
    """
    prompt = SQL_SYSTEM_PROMPT.format(schema=get_schema_text())
    prompt += f"\n\nQuestion: {question}\n"

    if error_feedback:
        prompt += (
            f"\nYour previous SQL failed with this error:\n{error_feedback}\n"
            "Fix the query and output only the corrected SQL."
        )

    prompt += "\nSQL:"

    response = _client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return _clean_sql(response.text)


if __name__ == "__main__":
    # quick manual check -- requires real network access, so only meaningful
    # when run outside this sandbox
    q = "What were the total sales in the West region in 2018?"
    print(generate_sql(q))
