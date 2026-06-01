import numpy as np
import pandas as pd

from src.constants import ISSUE_SEVERITY, PRODUCT_IMPACT


def aggregate_overview(df: pd.DataFrame) -> dict:
    return {
        "total_complaints": len(df),
        "top_product": df["Product"].value_counts().idxmax() if not df.empty else None,
        "top_issue": df["Issue"].value_counts().idxmax() if not df.empty else None,
        "top_state": df["State"].value_counts().idxmax() if not df.empty else None,
    }


def complaints_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Product").size().reset_index(name="count").sort_values("count", ascending=False)


def complaints_by_issue(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return df.groupby("Issue").size().reset_index(name="count").sort_values("count", ascending=False).head(top_n)


def complaints_by_state(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("State").size().reset_index(name="count").sort_values("count", ascending=False)


def complaints_by_company(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return df.groupby("Company").size().reset_index(name="count").sort_values("count", ascending=False).head(top_n)


def company_summary(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    summary = df.groupby("Company").agg(
        complaints=("Complaint ID", "count"),
        dispute_rate=("Consumer disputed?", lambda x: (x == "Yes").mean() * 100),
        timely_rate=("Timely response?", lambda x: (x == "Yes").mean() * 100),
        company_type=("Company type", lambda x: x.mode().iloc[0] if not x.mode().empty else "Other"),
    )
    summary = summary.reset_index()
    return summary.sort_values("complaints", ascending=False).head(top_n)


def company_type_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Company type").size().reset_index(name="count").sort_values("count", ascending=False)


def time_series(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Year-Month").size().reset_index(name="count").sort_values("Year-Month")


def company_risk_radar(df: pd.DataFrame, companies: list[str] | None = None) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["severity_score"] = df["Issue"].map(ISSUE_SEVERITY).fillna(0.6)
    df["impact_score"] = df["Product"].map(PRODUCT_IMPACT).fillna(0.6)
    df["escalation_score"] = df.apply(
        lambda row: 1.0 if row["Consumer disputed?"] == "Yes" else 0.75 if row["Timely response?"] == "No" else 0.4,
        axis=1,
    )

    grouped = df.groupby("Company").agg(
        complaints=("Complaint ID", "count"),
        dispute_rate=("Consumer disputed?", lambda x: (x == "Yes").mean() * 100),
        timely_rate=("Timely response?", lambda x: (x == "Yes").mean() * 100),
        avg_severity=("severity_score", "mean"),
        avg_impact=("impact_score", "mean"),
        avg_escalation=("escalation_score", "mean"),
    ).reset_index()

    grouped["complaint_volume"] = _normalize(grouped["complaints"])
    grouped["timely_response_risk"] = 100 - grouped["timely_rate"]
    grouped["dispute_risk"] = grouped["dispute_rate"]
    grouped["severity_risk"] = grouped["avg_severity"] * 100
    grouped["financial_impact_risk"] = grouped["avg_impact"] * 100
    grouped["escalation_risk"] = grouped["avg_escalation"] * 100
    grouped["overall_risk"] = _normalize(
        grouped[
            [
                "complaint_volume",
                "timely_response_risk",
                "dispute_risk",
                "severity_risk",
                "financial_impact_risk",
                "escalation_risk",
            ]
        ].mean(axis=1)
    )
    grouped["risk_label"] = grouped["overall_risk"].apply(_risk_label)

    if companies:
        grouped = grouped[grouped["Company"].isin(companies)]

    return grouped.sort_values("overall_risk", ascending=False)


def heatmap_product_issue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Product", "Issue"]) .size().reset_index(name="count").pivot(index="Product", columns="Issue", values="count").fillna(0)
    )


def state_risk_summary(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("State").agg(
        complaints=("Complaint ID", "count"),
        dispute_rate=("Consumer disputed?", lambda x: (x == "Yes").mean() * 100),
        timely_rate=("Timely response?", lambda x: (x == "Yes").mean() * 100),
        avg_severity=("Issue", lambda x: x.map(ISSUE_SEVERITY).fillna(0.6).mean() * 100),
    ).reset_index()
    grouped["timely_risk"] = 100 - grouped["timely_rate"]
    grouped["complaint_volume_norm"] = _normalize(grouped["complaints"])
    grouped["risk_score"] = _normalize(
        grouped["complaint_volume_norm"] * 0.35
        + grouped["dispute_rate"] * 0.25
        + grouped["timely_risk"] * 0.25
        + grouped["avg_severity"] * 0.15
    )
    grouped["risk_label"] = grouped["risk_score"].apply(_risk_label)
    return grouped.sort_values("risk_score", ascending=False)


def forecast_complaint_volume(
    df: pd.DataFrame,
    by: str = "Overall",
    value: str | None = None,
    periods: int = 6,
) -> dict:
    if df.empty:
        return {"history": pd.DataFrame(), "forecast": pd.DataFrame(), "debug": {}, "status": "no_data"}

    source = df if by == "Overall" or value is None else df[df[by] == value]
    source = source.copy()
    source["Date received"] = pd.to_datetime(source["Date received"], errors="coerce")
    source = source.dropna(subset=["Date received"])
    if source.empty:
        return {"history": pd.DataFrame(), "forecast": pd.DataFrame(), "debug": {}, "status": "no_data"}

    monthly = (
        source.groupby(pd.Grouper(key="Date received", freq="ME"))
        .size()
        .reset_index(name="count")
        .sort_values("Date received")
        .reset_index(drop=True)
    )
    if monthly.empty:
        return {"history": monthly, "forecast": pd.DataFrame(), "debug": {}, "status": "no_data"}

    monthly["Year-Month"] = monthly["Date received"].dt.to_period("M").astype(str)
    monthly["count"] = monthly["count"].astype(int)

    debug = {
        "min_date": monthly["Date received"].min(),
        "max_date": monthly["Date received"].max(),
        "monthly_points": len(monthly),
        "last_historical_month": monthly["Year-Month"].iloc[-1],
        "monthly_counts": monthly[["Year-Month", "count"]].to_dict(orient="records"),
    }

    if len(monthly) < periods:
        debug["first_forecast_month"] = None
        return {
            "history": monthly,
            "forecast": pd.DataFrame(),
            "debug": debug,
            "status": "not_enough_history",
        }

    monthly["period_index"] = range(len(monthly))
    x = monthly["period_index"].to_numpy(dtype=float)
    y = monthly["count"].to_numpy(dtype=float)

    coefs = np.polyfit(x, y, 1)
    predicted = np.polyval(coefs, x)
    residuals = y - predicted
    sigma = np.std(residuals, ddof=1) if len(residuals) > 1 else 0.0

    last_period = monthly["Date received"].iloc[-1]
    forecast_index = pd.date_range(start=last_period + pd.offsets.MonthEnd(1), periods=periods, freq="ME")
    debug["first_forecast_month"] = forecast_index[0].to_period("M").strftime("%Y-%m")

    forecast_rows = []
    for step, forecast_date in enumerate(forecast_index, start=1):
        pred_value = np.polyval(coefs, len(monthly) - 1 + step)
        lower = pred_value - 1.96 * sigma
        upper = pred_value + 1.96 * sigma
        forecast_rows.append(
            {
                "Date received": forecast_date,
                "Year-Month": forecast_date.to_period("M").strftime("%Y-%m"),
                "forecast": int(round(max(0, pred_value))),
                "lower": int(round(max(0, lower))),
                "upper": int(round(max(0, upper))),
            }
        )

    forecast = pd.DataFrame(forecast_rows)
    return {
        "history": monthly,
        "forecast": forecast,
        "debug": debug,
        "status": "ok",
    }


def company_scorecard(df: pd.DataFrame, company: str) -> dict | None:
    if company not in df["Company"].unique():
        return None
    radar = company_risk_radar(df, companies=[company])
    if radar.empty:
        return None
    row = radar.iloc[0]
    top_issues = (
        df[df["Company"] == company].groupby("Issue").size().reset_index(name="count").sort_values("count", ascending=False).head(3)
    )
    trend = _company_trend(df, company)
    return {
        "Company": company,
        "overall_risk": row["overall_risk"],
        "risk_label": row["risk_label"],
        "top_drivers": top_issues["Issue"].tolist(),
        "trend_direction": trend,
    }


def _company_trend(df: pd.DataFrame, company: str) -> str:
    company_df = df[df["Company"] == company]
    monthly = company_df.groupby("Year-Month").size().reset_index(name="count").sort_values("Year-Month")
    if len(monthly) < 2:
        return "Stable"
    last = monthly["count"].iloc[-1]
    prev = monthly["count"].iloc[-2]
    return "Rising" if last > prev else "Falling" if last < prev else "Stable"


def _normalize(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    minimum = series.min()
    maximum = series.max()
    if maximum == minimum:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((series - minimum) / (maximum - minimum) * 100).round(1)


def _risk_label(score: float) -> str:
    if pd.isna(score):
        return "Unknown"
    if score >= 81:
        return "High concern"
    if score >= 61:
        return "Elevated concern"
    if score >= 31:
        return "Moderate concern"
    return "Low concern"
