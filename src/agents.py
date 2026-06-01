import math
from typing import Any

import numpy as np
import pandas as pd

from src.constants import ISSUE_SEVERITY, PRODUCT_CATEGORIES


def _yes_rate(series: pd.Series) -> float:
    if series is None or len(series) == 0:
        return 0.0
    return (series.astype(str).str.strip().str.title() == "Yes").mean() * 100


def _no_rate(series: pd.Series) -> float:
    if series is None or len(series) == 0:
        return 0.0
    return (series.astype(str).str.strip().str.title() == "No").mean() * 100


def _safe_mean(series: pd.Series) -> float:
    if series is None or len(series.dropna()) == 0:
        return 0.0
    return float(series.dropna().astype(float).mean())


def _percent_change(current: float, prior: float) -> float:
    if prior == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - prior) / prior) * 100.0


def _normalize(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    minimum = series.min()
    maximum = series.max()
    if maximum == minimum:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((series - minimum) / (maximum - minimum) * 100).round(1)


def _risk_level(score: float) -> str:
    if score >= 65:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def analyze_risk_agent(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "highest_risk_company": "N/A",
            "top_risk_drivers": [],
            "risk_level": "Unknown",
            "risk_message": "Not enough data to evaluate risk signals.",
            "company_risk_table": pd.DataFrame(),
            "overall_risk_score": 0.0,
        }

    company_groups = df.groupby("Company")
    company_risks = []
    for company, group in company_groups:
        complaints = len(group)
        dispute_rate = _yes_rate(group["Consumer disputed?"])
        untimely_rate = _no_rate(group["Timely response?"])
        severity_score = _safe_mean(group.get("Complaint severity", group["Issue"].map(ISSUE_SEVERITY).fillna(0.6)))
        financial_impact = _safe_mean(group.get("Financial impact USD", pd.Series(dtype=float)))
        escalation_rate = ((group["Consumer disputed?"].astype(str).str.strip().str.title() == "Yes") |
                           (group["Timely response?"].astype(str).str.strip().str.title() == "No")).mean() * 100

        company_risks.append(
            {
                "Company": company,
                "complaints": complaints,
                "dispute_rate": round(dispute_rate, 1),
                "untimely_rate": round(untimely_rate, 1),
                "severity_score": round(severity_score, 1),
                "financial_impact": round(financial_impact, 1),
                "escalation_rate": round(escalation_rate, 1),
            }
        )

    risk_df = pd.DataFrame(company_risks)
    risk_df["complaint_norm"] = _normalize(risk_df["complaints"])
    risk_df["financial_norm"] = _normalize(risk_df["financial_impact"])
    risk_df["severity_norm"] = _normalize(risk_df["severity_score"])
    risk_df["overall_risk_score"] = (
        risk_df["complaint_norm"] * 0.28
        + risk_df["dispute_rate"] * 0.18
        + risk_df["untimely_rate"] * 0.18
        + risk_df["severity_norm"] * 0.16
        + risk_df["financial_norm"] * 0.1
        + risk_df["escalation_rate"] * 0.1
    )
    risk_df["risk_level"] = risk_df["overall_risk_score"].apply(_risk_level)
    risk_df = risk_df.sort_values("overall_risk_score", ascending=False)

    top_company = risk_df.iloc[0]
    high_issues = (
        df.groupby("Issue")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(3)
        ["Issue"]
        .tolist()
    )
    high_products = (
        df.groupby("Product")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(3)
        ["Product"]
        .tolist()
    )

    top_drivers = []
    if high_issues:
        top_drivers.append(high_issues[0])
    if len(high_products) > 0:
        top_drivers.append(high_products[0])
    if len(high_issues) > 1:
        top_drivers.append(high_issues[1])

    risk_message = (
        f"{top_company['Company']} leads the current filtered view with {int(top_company['complaints'])} complaints, "
        f"a dispute rate of {top_company['dispute_rate']:.1f}%, and an untimely response rate of {top_company['untimely_rate']:.1f}%. "
        f"Primary risk drivers are {', '.join(top_drivers[:3])}."
    )

    return {
        "highest_risk_company": top_company["Company"],
        "highest_risk_score": round(float(top_company["overall_risk_score"]), 1),
        "top_risk_drivers": top_drivers,
        "risk_level": top_company["risk_level"],
        "risk_message": risk_message,
        "company_risk_table": risk_df.head(6).reset_index(drop=True),
        "overall_risk_score": round(float(risk_df["overall_risk_score"].mean()), 1),
    }


def analyze_trend_agent(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "top_emerging_risks": [],
            "trend_direction": "Unknown",
            "percentage_change": 0.0,
            "trend_message": "Not enough data to identify trends.",
            "monthly_trend": pd.DataFrame(),
            "spike_details": {},
        }

    monthly = df.groupby("Year-Month").size().reset_index(name="count")
    monthly["Year-Month"] = pd.Categorical(monthly["Year-Month"], categories=sorted(monthly["Year-Month"].unique()), ordered=True)
    monthly = monthly.sort_values("Year-Month")

    product_growth = df.groupby(["Year", "Product"]).size().unstack(fill_value=0)
    issue_growth = df.groupby(["Year", "Issue"]).size().unstack(fill_value=0)
    state_growth = df.groupby(["Year", "State"]).size().unstack(fill_value=0)

    fastest_products = []
    fastest_issues = []
    emerging_states = []
    if len(product_growth.index) > 1:
        latest = product_growth.iloc[-1]
        prev = product_growth.iloc[-2]
        product_pct = ((latest - prev) / prev.replace(0, np.nan)).fillna(100.0).replace([np.inf, -np.inf], 100.0)
        fastest_products = pd.Series(product_pct).sort_values(ascending=False).head(3).index.tolist()
    if len(issue_growth.index) > 1:
        latest = issue_growth.iloc[-1]
        prev = issue_growth.iloc[-2]
        issue_pct = ((latest - prev) / prev.replace(0, np.nan)).fillna(100.0).replace([np.inf, -np.inf], 100.0)
        fastest_issues = pd.Series(issue_pct).sort_values(ascending=False).head(3).index.tolist()
    if len(state_growth.index) > 1:
        latest = state_growth.iloc[-1]
        prev = state_growth.iloc[-2]
        state_pct = ((latest - prev) / prev.replace(0, np.nan)).fillna(100.0).replace([np.inf, -np.inf], 100.0)
        emerging_states = pd.Series(state_pct).sort_values(ascending=False).head(2).index.tolist()

    spike_columns = []
    if len(monthly) > 1:
        monthly["delta"] = monthly["count"].diff().fillna(0)
        spike = monthly.sort_values("delta", ascending=False).iloc[0]
        spike_columns = [spike["Year-Month"], int(spike["count"]), int(spike["delta"])]

    trend_change = 0.0
    trend_direction = "Stable"
    if len(monthly) > 3:
        latest_three = monthly["count"].tail(3).sum()
        prior_three = monthly["count"].tail(6).head(3).sum()
        trend_change = _percent_change(latest_three, prior_three)
        if trend_change >= 15:
            trend_direction = "Rising"
        elif trend_change <= -10:
            trend_direction = "Declining"
        else:
            trend_direction = "Mixed"

    top_emerging = []
    for value in fastest_products[:2] + fastest_issues[:2] + emerging_states[:1]:
        if value not in top_emerging:
            top_emerging.append(value)
    if not top_emerging and fastest_products:
        top_emerging = fastest_products[:3]

    trend_message = (
        f"Recent filtered data shows {trend_direction.lower()} trends with a {trend_change:.1f}% change in the latest quarter. "
        f"Fastest-growing products include {', '.join(fastest_products[:2]) or 'N/A'}, and top rising issues include {', '.join(fastest_issues[:2]) or 'N/A'}."
    )

    return {
        "top_emerging_risks": top_emerging,
        "trend_direction": trend_direction,
        "percentage_change": round(trend_change, 1),
        "trend_message": trend_message,
        "monthly_trend": monthly,
        "spike_details": {
            "month": spike_columns[0] if spike_columns else "N/A",
            "volume": spike_columns[1] if spike_columns else 0,
            "increase": spike_columns[2] if spike_columns else 0,
        },
    }


def analyze_consumer_agent(df: pd.DataFrame, risk_result: dict[str, Any], trend_result: dict[str, Any]) -> dict[str, Any]:
    if df.empty:
        return {
            "safety_index": 0.0,
            "watch_items": [],
            "risky_categories": [],
            "warning_signs": [],
            "recommendations": [],
            "consumer_message": "No consumer guidance is available for an empty dataset.",
        }

    dispute_rate = _yes_rate(df["Consumer disputed?"])
    untimely_rate = _no_rate(df["Timely response?"])
    escalation_rate = ((df["Consumer disputed?"].astype(str).str.strip().str.title() == "Yes") |
                       (df["Timely response?"].astype(str).str.strip().str.title() == "No")).mean() * 100
    top_products = df["Product"].value_counts().head(3).index.tolist()
    top_issues = df["Issue"].value_counts().head(3).index.tolist()

    safety_index = max(0.0, 100.0 - ((dispute_rate * 0.35) + (untimely_rate * 0.35) + (escalation_rate * 0.3)))
    risky_categories = top_products
    watch_items = [f"{top_issues[0]}" if top_issues else "Unknown issue"]
    warning_signs = []
    if dispute_rate > 20:
        warning_signs.append("High dispute activity among filtered complaints")
    if untimely_rate > 20:
        warning_signs.append("Elevated untimely response rate from companies")
    if escalation_rate > 30:
        warning_signs.append("Many complaints show escalation or dispute patterns")
    if not warning_signs:
        warning_signs.append("No immediate warning sign crosses a high-risk threshold, but continue monitoring trends.")

    recommendations = [
        "Compare company response performance before escalating a complaint.",
        "Pay attention to product categories with repeated dispute or delayed response issues.",
        "Document interactions and keep a record if you need to escalate a complaint.",
    ]

    consumer_message = (
        f"Filtered consumer intelligence points to {', '.join(risky_categories[:2])} as the most impacted categories. "
        f"Watch for {watch_items[0] if watch_items else 'persistent complaint themes'} and prefer companies with faster response performance."
    )

    return {
        "safety_index": round(safety_index, 1),
        "watch_items": watch_items,
        "risky_categories": risky_categories,
        "warning_signs": warning_signs,
        "recommendations": recommendations,
        "consumer_message": consumer_message,
    }


def synthesize_executive_agent(
    risk_result: dict[str, Any],
    trend_result: dict[str, Any],
    consumer_result: dict[str, Any],
) -> dict[str, Any]:
    if not risk_result or not trend_result or not consumer_result:
        return {
            "top_findings": [],
            "key_risks": [],
            "recommended_actions": [],
            "confidence_level": "Unknown",
            "summary_bullets": [],
        }

    top_findings = [
        f"{risk_result['highest_risk_company']} is the top risk company with a {risk_result['risk_level']} risk profile.",
        f"Emerging risks include {', '.join(trend_result['top_emerging_risks'][:3]) or 'N/A'}.",
        f"Consumer safety is estimated at {consumer_result['safety_index']}% for the current filtered view.",
    ]
    key_risks = [
        f"{risk_result['risk_level']} risk at {risk_result['highest_risk_company']}.",
        f"Rapid growth in {', '.join(trend_result['top_emerging_risks'][:2]) or 'products/issues'}.",
        f"Consumer warning signs: {', '.join(consumer_result['warning_signs'][:2])}.",
    ]
    recommended_actions = [
        "Monitor the highest risk companies and investigate repeated dispute patterns.",
        "Focus on emerging products/issues with accelerating complaint growth.",
        "Provide consumers with clear guidance on response expectations and escalation options.",
    ]
    confidence_level = "High" if len(trend_result.get("top_emerging_risks", [])) > 0 and len(risk_result.get("top_risk_drivers", [])) > 0 else "Moderate"
    summary_bullets = [
        top_findings[0],
        top_findings[1],
        top_findings[2],
    ]

    return {
        "top_findings": top_findings,
        "key_risks": key_risks,
        "recommended_actions": recommended_actions,
        "confidence_level": confidence_level,
        "summary_bullets": summary_bullets,
    }


def build_briefing_markdown(
    risk_result: dict[str, Any],
    trend_result: dict[str, Any],
    consumer_result: dict[str, Any],
    executive_result: dict[str, Any],
) -> str:
    lines = [
        "# AI Command Center Briefing",
        "",
        "## Executive summary",
    ]
    for bullet in executive_result.get("summary_bullets", []):
        lines.append(f"- {bullet}")
    lines.extend([
        "",
        "## Risk Agent findings",
        f"- Highest-risk company: {risk_result.get('highest_risk_company', 'N/A')}",
        f"- Risk level: {risk_result.get('risk_level', 'N/A')}",
        f"- Top risk drivers: {', '.join(risk_result.get('top_risk_drivers', []))}",
        f"- Analyst note: {risk_result.get('risk_message', '')}",
        "",
        "## Trend Agent findings",
        f"- Trend direction: {trend_result.get('trend_direction', 'N/A')}",
        f"- Change: {trend_result.get('percentage_change', 0.0):.1f}%",
        f"- Emerging risks: {', '.join(trend_result.get('top_emerging_risks', []))}",
        f"- Trend note: {trend_result.get('trend_message', '')}",
        "",
        "## Consumer Impact Agent guidance",
        f"- Safety index: {consumer_result.get('safety_index', 0.0):.1f}%",
        f"- Watch items: {', '.join(consumer_result.get('watch_items', []))}",
        f"- Recommended actions: {', '.join(consumer_result.get('recommendations', []))}",
        f"- Consumer note: {consumer_result.get('consumer_message', '')}",
        "",
        "## Recommendations",
    ])
    for action in executive_result.get("recommended_actions", []):
        lines.append(f"- {action}")
    lines.extend([
        "",
        f"Confidence level: {executive_result.get('confidence_level', 'Moderate')}",
    ])
    return "\n".join(lines)


def generate_ai_command_center(df: pd.DataFrame) -> dict[str, Any]:
    risk = analyze_risk_agent(df)
    trend = analyze_trend_agent(df)
    consumer = analyze_consumer_agent(df, risk, trend)
    executive = synthesize_executive_agent(risk, trend, consumer)
    briefing_md = build_briefing_markdown(risk, trend, consumer, executive)
    return {
        "risk": risk,
        "trend": trend,
        "consumer": consumer,
        "executive": executive,
        "briefing_markdown": briefing_md,
    }
