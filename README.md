## Live Demo

Try the application here (PLEASE TURN ON VPN):

👉 https://ai-business-analyst-bocztyyqfshkc76yonadsr.streamlit.app/

The demo allows users to ask business questions in natural language and receive SQL analysis, insights, and visualizations.
# AI Business Analyst

An AI-powered business analysis assistant that allows users to ask questions about business data using natural language and receive insights, SQL queries, and visual analysis.

The project demonstrates how Large Language Models (LLMs) can be integrated with traditional data systems to create a reliable and transparent business analyst workflow.

Instead of directly giving database access to an AI model, the system uses a controlled pipeline for SQL generation, validation, execution, and insight generation.

---

## Overview

AI Business Analyst converts business questions into structured data analysis.

A user can ask questions such as:

* "What are the top customers by number of tickets?"
* "Which categories have the highest issue volume?"
* "How has ticket activity changed over time?"

The system analyzes the request, generates a safe SQL query, executes it against the database, and explains the results in a business-friendly format.

---

## Architecture

The project follows a modular agent-based architecture:

```
User Question
      |
      v
SQL Generator (LLM)
      |
      v
SQL Validator
      |
      v
Database Executor
      |
      v
Insight Generator (LLM)
      |
      v
Charts & Business Report
```

Each component has a specific responsibility, making the system easier to maintain, test, and extend.

---

# Key Features

##  Natural Language to SQL

The system uses Gemini to translate business questions into SQL queries.

The model receives:

* Database schema information
* Table relationships
* SQL generation rules
* User question

This allows the model to generate queries based on the actual database structure.

---

##  SQL Validation & Safety Layer

Generated SQL is never executed directly.

Before execution, every query passes through a validation layer that checks:

* Query must start with `SELECT`
* Dangerous SQL operations are blocked
* Multiple statements are prevented
* Unsafe keywords are rejected

This ensures that the AI model cannot accidentally modify or damage the database.

---

##  Automatic SQL Error Recovery

If a generated query fails because of syntax errors or incorrect assumptions, the system sends the error feedback back to the model.

The agent can then attempt to generate a corrected query.

Workflow:

```
Generate SQL
      |
Validate
      |
Execute
      |
Error?
      |
Send feedback
      |
Retry
```

---

##  Automatic Insight Generation

After retrieving data, another AI component converts raw results into understandable business insights.

Instead of showing only numbers and tables, the system explains:

* What happened
* Possible patterns
* Important observations
* Business implications

The output is designed for non-technical users.

---

##  Smart Visualization

The chart generation module uses rule-based logic instead of AI.

Based on the returned data:

* Time-based data → Line chart
* Category comparison → Bar chart
* Single values → No unnecessary visualization

This keeps the system faster, cheaper, and more predictable.

---

# Project Structure

```
ai-business-analyst/
│
├── agent/
│   ├── sql_generator.py
│   ├── validator.py
│   ├── executor.py
│   ├── insight_generator.py
│   └── charts.py
│
├── database/
│   ├── db_setup.py
│   └── schema.py
│
├── utils/
│   └── config.py
│
└── app/
    └── streamlit_app.py
```

---

# Technology Stack

* Python
* Google Gemini API
* SQLite
* Streamlit
* Pandas
* Plotly
* SQL
* Prompt Engineering

---

# Running the Project

Clone the repository:

```bash
git clone https://github.com/ala1382hoseini-del/ai-business-analyst.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
GEMINI_API_KEY=your_api_key
```

Run the application:

```bash
streamlit run app/streamlit_app.py
```

---

# Design Principles

This project was built around a few important principles:

### Separation of Responsibilities

Each module has one clear responsibility:

* Database setup handles data
* Schema describes database structure
* SQL generator communicates with the LLM
* Validator protects the database
* Executor manages the workflow
* Insight generator explains results
* Charts handle visualization

### Fail Fast

Configuration errors and invalid states are detected early with clear messages.

### AI with Guardrails

The model is used where reasoning is valuable, while deterministic rules handle security-critical decisions.

---

# Future Improvements

Possible improvements:

* Multi-agent collaboration
* Support for multiple databases
* User authentication
* Conversation memory
* More business analysis frameworks (SWOT, BMC, PESTEL)
* Advanced dashboards
* Data source connectors

---

# Author

Created by **ala1382hoseini-del**

GitHub:
https://github.com/ala1382hoseini-del
