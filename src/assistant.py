import pandas as pd

from src.analytics import (
    company_risk_radar,
    complaints_by_issue,
    complaints_by_product,
    state_risk_summary,
)
from src.constants import AI_SUMMARY_TEMPLATES


def _question_contains(question: str, any_terms: list[str], all_terms: list[str] | None = None) -> bool:
    if all_terms is None:
        all_terms = []
    return any(term in question for term in any_terms) and all(term in question for term in all_terms)


def _companies_mentioned(df: pd.DataFrame, question: str) -> list[str]:
    mentioned = []
    for company in sorted(df["Company"].dropna().unique(), key=len, reverse=True):
        if company.lower() in question:
            mentioned.append(company)
    return mentioned


def answer_question(df: pd.DataFrame, question: str) -> dict:
    q = question.lower().strip()
    if not q:
        return {"summary": "Please type a data question to get started.", "chart": None}
    if df.empty:
        return {"summary": "No complaint data is available for the current filters.", "chart": None}

    mentioned_companies = _companies_mentioned(df, q)
    if len(mentioned_companies) >= 2 and any(term in q for term in ["compare", "compared", "versus", " vs "]):
        companies = mentioned_companies[:2]
        comparison = df[df["Company"].isin(companies)].groupby("Company").agg(
            complaints=("Complaint ID", "count"),
            dispute_rate=("Consumer disputed?", lambda x: (x == "Yes").mean() * 100),
            timely_rate=("Timely response?", lambda x: (x == "Yes").mean() * 100),
        ).reset_index()
        radar = company_risk_radar(df, companies=companies)[["Company", "overall_risk", "risk_label"]]
        comparison = comparison.merge(radar, on="Company", how="left")
        comparison["question_order"] = comparison["Company"].apply(companies.index)
        comparison = comparison.sort_values("question_order").drop(columns="question_order")

        if comparison.empty:
            return {"summary": "No company comparison data is available in the current filtered view.", "chart": None}

        first = comparison.iloc[0]
        second = comparison.iloc[1]
        higher = comparison.sort_values("overall_risk", ascending=False).iloc[0]
        summary = (
            f"{first['Company']} has {int(first['complaints'])} complaints, a {first['dispute_rate']:.1f}% dispute rate, "
            f"and a {first['timely_rate']:.1f}% timely response rate. "
            f"{second['Company']} has {int(second['complaints'])} complaints, a {second['dispute_rate']:.1f}% dispute rate, "
            f"and a {second['timely_rate']:.1f}% timely response rate. "
            f"On the overall risk score, {higher['Company']} is higher at {higher['overall_risk']:.1f} ({higher['risk_label']})."
        )
        return {
            "summary": summary,
            "chart": {
                "type": "bar",
                "data": comparison,
                "x": "Company",
                "y": "complaints",
                "title": "Company complaint comparison",
            },
        }

    if "fraud" in q:
        fraud = df[df["Issue"].str.contains("fraud", case=False, na=False)]
        if fraud.empty:
            return {"summary": "No fraud-related complaints were found in the current dataset.", "chart": None}
        top = fraud.groupby("Company").size().reset_index(name="count").sort_values("count", ascending=False)
        company = top.iloc[0]["Company"]
        summary = f"{company} has the highest fraud complaint volume in the current filtered view, with {top.iloc[0]['count']} fraud-related records."
        return {"summary": summary, "chart": {"type": "bar", "data": top.head(10), "x": "Company", "y": "count"}}

    if _question_contains(q, ["response", "timely"], ["worst"]) or _question_contains(q, ["response rate", "timely response"], None) or "late" in q:
        rates = df.groupby("Product").agg(
            timely_rate=("Timely response?", lambda x: (x == "Yes").mean() * 100),
            count=("Complaint ID", "count"),
        ).reset_index()
        rates["risk"] = 100 - rates["timely_rate"]
        worst = rates.sort_values("risk", ascending=False).head(5)
        summary = f"The products with the weakest timely response performance are {', '.join(worst['Product'].head(3).tolist())}."
        return {"summary": summary, "chart": {"type": "bar", "data": worst, "x": "Product", "y": "risk"}}

    if "2025" in q or "changed most" in q or "grew the most" in q:
        if "Year" not in df.columns:
            return {"summary": "Year information is unavailable for this data set.", "chart": None}
        year_2025 = df[df["Year"] == 2025]
        prior = df[df["Year"] == 2024]
        if year_2025.empty or prior.empty:
            return {"summary": "There is not enough data to compare 2025 with the prior year.", "chart": None}
        comparison = (
            year_2025.groupby("Product").size().reset_index(name="count_2025")
            .merge(prior.groupby("Product").size().reset_index(name="count_2024"), on="Product", how="outer")
            .fillna(0)
        )
        comparison["pct_change"] = comparison.apply(
            lambda row: (row["count_2025"] - row["count_2024"]) / max(row["count_2024"], 1) * 100,
            axis=1,
        )
        top = comparison.sort_values("pct_change", ascending=False).head(5)
        leader = top.iloc[0]
        summary = f"In 2025, {leader['Product']} grew the most versus 2024, rising by {leader['pct_change']:.1f}% in complaint volume."
        return {"summary": summary, "chart": {"type": "bar", "data": top, "x": "Product", "y": "pct_change"}}

    if _question_contains(q, ["issue"], ["most"]) or _question_contains(q, ["most frequent issue"], None) or _question_contains(q, ["top issue"], None):
        issue_counts = complaints_by_issue(df, top_n=10)
        if issue_counts.empty:
            return {"summary": "No issue data is available in the current filtered view.", "chart": None}
        top_issue = issue_counts.iloc[0]
        summary = f"The most frequent issue in the current filtered data is {top_issue['Issue']} with {top_issue['count']} complaints."
        return {"summary": summary, "chart": {"type": "bar", "data": issue_counts, "x": "Issue", "y": "count"}}

    if _question_contains(q, ["product"], ["top"]) or _question_contains(q, ["most common product"], None):
        products = complaints_by_product(df)
        if products.empty:
            return {"summary": "No product data is available in the current filtered view.", "chart": None}
        top_product = products.iloc[0]
        summary = f"The most complained-about product is {top_product['Product']} with {top_product['count']} complaints."
        return {"summary": summary, "chart": {"type": "bar", "data": products.head(10), "x": "Product", "y": "count"}}

    if _question_contains(q, ["state"], ["top"]) or _question_contains(q, ["most complaints", "state"], None):
        states = state_risk_summary(df).sort_values("complaints", ascending=False).head(10)
        if states.empty:
            return {"summary": "No state-level data is available in the current filtered view.", "chart": None}
        top_state = states.iloc[0]
        summary = f"The state with the highest complaint volume in the current view is {top_state['State']} with {int(top_state['complaints'])} complaints."
        return {"summary": summary, "chart": {"type": "bar", "data": states, "x": "State", "y": "complaints"}}

    if _question_contains(q, ["company", "risk"], None) or _question_contains(q, ["institution", "risk"], None) or "major risk" in q:
        radar = company_risk_radar(df).sort_values("overall_risk", ascending=False).head(5)
        if radar.empty:
            return {"summary": "No company risk breakdown is available for this filtered data.", "chart": None}
        company_list = ", ".join(radar["Company"].head(3).tolist())
        summary = f"The highest risk institutions in the current view are {company_list}, mainly driven by elevated complaint volume and dispute risk."
        return {"summary": summary, "chart": {"type": "bar", "data": radar.head(10), "x": "Company", "y": "overall_risk"}}

    return {
        "summary": "I can answer questions about fraud complaints, response rates, changes in 2025, issue frequency, top products, and top risk companies. Please refine your query.",
        "chart": None,
    }


def build_executive_summary(df: pd.DataFrame, filters: dict) -> list[str]:
    if df.empty:
        return ["No data is available for the selected filters."]

    top_state = df["State"].mode().iloc[0] if not df["State"].empty else "N/A"
    top_product = df["Product"].mode().iloc[0] if not df["Product"].empty else "N/A"
    top_issue = df["Issue"].mode().iloc[0] if not df["Issue"].empty else "N/A"
    state_summary = state_risk_summary(df).head(3)
    high_risk = ", ".join(state_summary["State"].head(3).tolist())

    return [
        AI_SUMMARY_TEMPLATES["major_trends"].format(
            top_state=top_state,
            top_product=top_product,
            top_issue=top_issue,
        ),
        AI_SUMMARY_TEMPLATES["unusual_spike"].format(
            issue_or_state=top_issue,
        ),
        AI_SUMMARY_TEMPLATES["high_risk_institutions"].format(
            company_list=high_risk,
        ),
        AI_SUMMARY_TEMPLATES["consumer_implications"].format(
            risk_theme="delayed response and elevated dispute risk",
        ),
    ]
