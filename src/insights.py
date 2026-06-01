import pandas as pd

from src.constants import INSIGHT_TEMPLATES
from src.analytics import complaints_by_issue, complaints_by_product


def build_insights(df: pd.DataFrame, top_n: int = 3) -> list[str]:
    if df.empty:
        return ["No complaint data is available for the selected filters."]

    insights = []
    overview = {
        "product": df["Product"].mode().iloc[0] if not df["Product"].empty else "N/A",
        "count": int(df["Product"].value_counts().iloc[0]) if not df.empty else 0,
        "issue": df["Issue"].mode().iloc[0] if not df["Issue"].empty else "N/A",
        "pct": 0.0,
        "state": df["State"].mode().iloc[0] if not df["State"].empty else "N/A",
    }
    issue_counts = complaints_by_issue(df, top_n=top_n)
    if not issue_counts.empty:
        overview["pct"] = issue_counts.iloc[0]["count"] / len(df) * 100

    insights.append(INSIGHT_TEMPLATES["top_product"].format(**overview))
    insights.append(INSIGHT_TEMPLATES["top_issue"].format(**overview))
    insights.append(INSIGHT_TEMPLATES["top_state"].format(**overview))

    company_type_insight = _top_company_type(df)
    if company_type_insight is not None:
        insights.append(
            f"{company_type_insight['company_type']} companies represent the largest complaint share with {company_type_insight['percent']:.1f}% of filtered complaints."
        )

    product_growth = _top_growth_product(df)
    if product_growth is not None:
        insights.append(
            INSIGHT_TEMPLATES["rising_product"].format(
                product=product_growth["Product"], growth=product_growth["growth"]
            )
        )

    dispute_rates = _top_dispute_rate(df)
    if dispute_rates is not None:
        insights.append(
            INSIGHT_TEMPLATES["dispute_rate"].format(
                product=dispute_rates["Product"], pct=dispute_rates["dispute_rate"]
            )
        )

    return insights


def _top_company_type(df: pd.DataFrame) -> dict | None:
    grouped = df.groupby("Company type").size().reset_index(name="count")
    if grouped.empty:
        return None
    top = grouped.sort_values("count", ascending=False).iloc[0]
    return {
        "company_type": top["Company type"],
        "percent": top["count"] / len(df) * 100,
    }


def _top_growth_product(df: pd.DataFrame) -> dict | None:
    grouped = df.groupby("Product").agg(
        count=("Complaint ID", "count"),
        last_month=("Year-Month", lambda x: _period_count(x, -1)),
        prior_month=("Year-Month", lambda x: _period_count(x, -2)),
    ).reset_index()
    grouped["growth"] = (
        (grouped["last_month"] - grouped["prior_month"]) / grouped["prior_month"].replace({0: 1}) * 100
    )
    top = grouped.sort_values("growth", ascending=False).head(1)
    if top.empty:
        return None
    return top.iloc[0].to_dict()


def _top_dispute_rate(df: pd.DataFrame) -> dict | None:
    grouped = df.groupby("Product").agg(
        dispute_rate=("Consumer disputed?", lambda x: (x == "Yes").mean() * 100)
    ).reset_index()
    top = grouped.sort_values("dispute_rate", ascending=False).head(1)
    if top.empty:
        return None
    return top.iloc[0].to_dict()


def _period_count(series: pd.Series, position: int) -> int:
    periods = series.sort_values().unique()
    if len(periods) < abs(position):
        return 0
    target = periods[position]
    return (series == target).sum()
