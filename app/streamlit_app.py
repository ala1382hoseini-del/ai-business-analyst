"""
streamlit_app.py
------------------
The user-facing UI for the AI Business Analyst agent.

Run with:
    streamlit run app/streamlit_app.py
(from the project root)
"""

import sys
import os

# Allow running this file directly with `streamlit run app/streamlit_app.py`
# by making sure the project root is on sys.path (Streamlit doesn't run
# files as part of a package the way `python -m` does).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from agent.executor import answer_question
from agent.insight_generator import generate_insight
from agent.charts import build_chart

st.set_page_config(page_title="AI Business Analyst", page_icon="📊", layout="centered")

st.title("📊 AI Business Analyst")
st.caption(
    "Ask a question about the support ticketing data in plain language — "
    "the agent writes the SQL, runs it, and explains the result."
)

with st.expander("Example questions"):
    st.markdown(
        "- How many tickets are currently open?\n"
        "- Which agent has closed the most tickets?\n"
        "- What is the average resolution time in days?\n"
        "- Show ticket count by priority.\n"
        "- Which product has the most critical severity tickets?\n"
        "- Which customer has filed the most tickets?"
    )

question = st.text_input("Your question", placeholder="e.g. What were total sales by region?")
ask_clicked = st.button("Ask", type="primary")

if ask_clicked and question.strip():
    with st.spinner("Thinking..."):
        result = answer_question(question)

    if result["status"] == "cannot_answer":
        st.warning(
            "This question can't be answered with the available data "
            "(e.g. it may ask about profit, discount, or quantity, which "
            "aren't in this dataset)."
        )

    elif result["status"] == "failed":
        st.error(
            f"Sorry, I couldn't generate a working query for that question "
            f"after {result['attempts']} attempt(s)."
        )
        with st.expander("Technical details"):
            st.code(result.get("sql") or "(no SQL generated)", language="sql")
            st.text(result.get("error", ""))

    else:  # success
        df = result["data"]

        with st.spinner("Summarizing..."):
            insight_text = generate_insight(question, df)

        st.markdown("### Answer")
        st.write(insight_text)

        fig = build_chart(df)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("View data and generated SQL"):
            st.code(result["sql"], language="sql")
            st.dataframe(df, use_container_width=True)

        if result["attempts"] > 1:
            st.caption(f"(Took {result['attempts']} attempts to get a valid query.)")

elif ask_clicked:
    st.info("Please enter a question first.")
