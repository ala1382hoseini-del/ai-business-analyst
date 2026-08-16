"""
charts.py
----------
Simple, rule-based logic for deciding whether a query result is
chart-worthy, and if so, building an appropriate Plotly figure.

Deliberately rule-based (not another LLM call) for v1: fast, free,
predictable, and good enough for the shapes of data a business-analyst
question typically returns. Smarter chart-type selection can move to v2.
"""

import pandas as pd
import plotly.express as px

MAX_CATEGORIES_FOR_CHART = 25


def _is_date_like(series: pd.Series) -> bool:
    import warnings

    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    sample = series.dropna().head(5)
    if sample.empty or not sample.map(lambda v: isinstance(v, str)).all():
        return False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pd.to_datetime(sample, errors="raise")
        return True
    except (ValueError, TypeError):
        return False


def build_chart(data: pd.DataFrame):
    """
    Returns a Plotly figure if the data is chart-worthy, else None.

    Rules:
      - A single-cell result (one row, one column) -> no chart, it's just
        a headline number.
      - Exactly 2 columns, one categorical + one numeric, few enough rows
        -> bar chart.
      - A date/time column + one numeric column -> line chart.
      - Anything else (too many columns, too many rows, no numeric
        column) -> no chart, table is clearer.
    """
    if data is None or data.empty:
        return None

    if data.shape == (1, 1):
        return None

    if data.shape[1] != 2:
        return None

    col_a, col_b = data.columns[0], data.columns[1]
    numeric_cols = data.select_dtypes(include="number").columns.tolist()

    if len(numeric_cols) != 1:
        return None

    value_col = numeric_cols[0]
    label_col = col_b if value_col == col_a else col_a

    if len(data) > MAX_CATEGORIES_FOR_CHART:
        return None

    if _is_date_like(data[label_col]):
        fig = px.line(data, x=label_col, y=value_col, markers=True)
    else:
        fig = px.bar(data, x=label_col, y=value_col)

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
    )
    return fig


if __name__ == "__main__":
    df1 = pd.DataFrame({"total_sales": [710219.6]})
    df2 = pd.DataFrame({
        "region": ["East", "West", "Central", "South"],
        "total_sales": [678781.2, 710219.6, 501239.9, 391721.9],
    })
    print("Single value -> chart?", build_chart(df1))
    print("Category breakdown -> chart?", build_chart(df2) is not None)
