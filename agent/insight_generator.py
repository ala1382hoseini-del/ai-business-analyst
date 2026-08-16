"""
insight_generator.py
----------------------
Takes the raw query result (a DataFrame) plus the original question and
asks Gemini to summarize it the way a business analyst would explain it
to a non-technical manager -- not just restate the numbers.
"""

import pandas as pd
from google import genai
from utils.config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)

INSIGHT_PROMPT_TEMPLATE = """You are a business analyst explaining a query
result to a non-technical manager.

Original question: {question}

Query result (as a table):
{table}

Write a short, natural-language answer (2-4 sentences):
- Directly answer the question first.
- Add one relevant observation if something in the data stands out
  (e.g. a clear leader, a surprising gap), but don't invent numbers that
  aren't in the table.
- Do not mention SQL, databases, or that you are an AI.
- Do not use markdown formatting -- no backticks, no bold, no bullet
  points. Plain sentences only, since this is displayed as plain text.
- Be concise and confident, like a real analyst reporting a finding.
"""


def generate_insight(question: str, data: pd.DataFrame) -> str:
    if data is None or data.empty:
        return "برای این سوال هیچ داده‌ای در نتیجه پیدا نشد."

    # Cap how much data we send to the model -- for large result sets we
    # only need a representative sample to summarize, not everything.
    table_text = data.head(20).to_string(index=False)
    if len(data) > 20:
        table_text += f"\n... ({len(data) - 20} more rows not shown)"

    prompt = INSIGHT_PROMPT_TEMPLATE.format(question=question, table=table_text)

    response = _client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text.strip()


if __name__ == "__main__":
    sample_df = pd.DataFrame({"total_sales": [710219.6]})
    print(generate_insight("What were the total sales in the West region?", sample_df))
