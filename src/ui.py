import os
from html import escape
from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st

from src.constants import APP_DESCRIPTION, APP_NAME, BRAND_PALETTE, PRODUCT_CATEGORIES, STATE_ABBREVIATIONS

PLOTLY_AVAILABLE = True
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ModuleNotFoundError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp { background-color: #f5f7fb; }
            .app-header { padding: 1rem 0; }
            .title-bar { display: flex; align-items: center; gap: 1rem; }
            .brand-pill { background: #0f4c81; color: white; padding: 0.35rem 0.8rem; border-radius: 999px; font-size: 0.95rem; letter-spacing: 0.04em; }
            .section-card { padding: 1.2rem; border-radius: 16px; background: #ffffff; box-shadow: 0 10px 20px rgba(15, 76, 129, 0.08); }
            section[data-testid="stSidebar"] > div { background-color: #ffffff !important; }
            .stSidebar .css-1offfwp, .stSidebar .css-1offfwp * { background-color: #ffffff !important; }
            .sidebar .stButton>button, [data-testid="stDownloadButton"] button { width: 100%; }
            .big-number { font-size: 2.5rem; font-weight: 700; color: #0f4c81; }
            .card-title { font-size: 1rem; font-weight: 600; color: #0f4c81; margin-bottom: 0.25rem; }
            .card-value { font-size: 1.8rem; font-weight: 700; color: #264653; }
            h1, h2, h3, h4, h5, h6 { color: #0f4c81; }
            .stMarkdown p, .stText, .stTextInput>div>label { color: #273846; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header() -> None:
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.svg")
    with st.container():
        col1, col2 = st.columns([1, 5])
        with col1:
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
        with col2:
            st.markdown(
                f"<div class='app-header'><div class='title-bar'><div class='brand-pill'>RADAR</div><h1 style='margin:0'>{APP_NAME}</h1></div><p style='margin:0.5rem 0 0.5rem 0; color:#4d4d4d;'>{APP_DESCRIPTION}</p></div>",
                unsafe_allow_html=True,
            )


STATE_NAME_TO_CODE = {name: code for code, name in STATE_ABBREVIATIONS.items()}


def state_to_plotly_location(state: str) -> str | None:
    if not isinstance(state, str):
        return None
    state = state.strip()
    upper = state.upper()
    if upper in STATE_ABBREVIATIONS:
        return upper
    return STATE_NAME_TO_CODE.get(state.title())


def render_filters(df: pd.DataFrame) -> dict:
    min_date = df["Date received"].min()
    max_date = df["Date received"].max()

    st.sidebar.markdown("### Filter complaints")
    st.sidebar.caption("Use the filters below to narrow the dashboard analysis.")
    date_selection = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_selection, (list, tuple)):
        if len(date_selection) == 2:
            start_date, end_date = date_selection
        elif len(date_selection) == 1:
            start_date = end_date = date_selection[0]
        else:
            start_date, end_date = min_date, max_date
    elif date_selection is None:
        start_date, end_date = min_date, max_date
    else:
        start_date = end_date = date_selection

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    year = st.sidebar.multiselect(
        "Year",
        options=sorted(df["Year"].dropna().astype(str).unique()),
        default=sorted(df["Year"].dropna().astype(str).unique()),
    )
    product = st.sidebar.selectbox("Product category", ["All"] + PRODUCT_CATEGORIES, index=0)
    state = st.sidebar.multiselect(
        "State",
        options=sorted(df["State"].dropna().unique()),
        default=[],
    )
    company = st.sidebar.multiselect(
        "Company",
        options=sorted(df["Company"].dropna().unique()),
        default=[],
    )
    issue = st.sidebar.multiselect(
        "Issue",
        options=sorted(df["Issue"].dropna().unique()),
        default=[],
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### Dashboard metrics")
    return {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "product": product,
        "state": state,
        "company": company,
        "issue": issue,
    }


def render_dataset_summary(df: pd.DataFrame, warnings: list) -> None:
    st.sidebar.metric("Records", len(df))
    st.sidebar.metric("Companies", df["Company"].nunique())
    st.sidebar.metric("Issues", df["Issue"].nunique())
    for index, message in enumerate(warnings):
        if index == 0:
            st.sidebar.success(message)
        else:
            st.sidebar.warning(message)
    st.sidebar.markdown("---")


def render_filter_summary(filters: dict) -> None:
    st.markdown("#### Active filters")
    start_date = filters["start_date"].strftime("%Y-%m-%d")
    end_date = filters["end_date"].strftime("%Y-%m-%d")
    product = filters["product"]
    state = ", ".join(filters["state"]) if filters["state"] else "All states"
    company = ", ".join(filters["company"]) if filters["company"] else "All companies"
    issue = ", ".join(filters["issue"]) if filters["issue"] else "All issues"
    year = ", ".join(filters["year"]) if filters["year"] else "All years"

    st.info(
        f"**Date range:** {start_date} to {end_date}  \
        **Year:** {year}  \
        **Product:** {product}  \
        **States:** {state}  \
        **Companies:** {company}  \
        **Issues:** {issue}",
        icon="ℹ️",
    )


def render_download_button(df: pd.DataFrame) -> None:
    if df.empty:
        return
    csv = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="Download filtered dataset",
        data=csv,
        file_name="complaint_radar_filtered.csv",
        mime="text/csv",
    )


def filter_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    filtered = df[
        (df["Date received"] >= filters["start_date"]) &
        (df["Date received"] <= filters["end_date"])
    ]
    if filters["year"]:
        filtered = filtered[filtered["Year"].astype(str).isin(filters["year"])]
    if filters["product"] != "All":
        filtered = filtered[filtered["Product"] == filters["product"]]
    if filters["state"]:
        filtered = filtered[filtered["State"].isin(filters["state"])]
    if filters["company"]:
        filtered = filtered[filtered["Company"].isin(filters["company"])]
    if filters["issue"]:
        filtered = filtered[filtered["Issue"].isin(filters["issue"])]
    return filtered


def render_overview_cards(metrics: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total complaints", metrics.get("total_complaints", 0))
    col2.metric("Top product", metrics.get("top_product", "N/A"))
    col3.metric("Top issue", metrics.get("top_issue", "N/A"))
    col4.metric("Top state", metrics.get("top_state", "N/A"))


def render_time_series(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No data available for the selected filters.")
        return
    chart = alt.Chart(df).mark_line(point=True, color=BRAND_PALETTE[0], strokeWidth=3).encode(
        x=alt.X("Year-Month:T", title="Month"),
        y=alt.Y("count:Q", title="Complaint count"),
        tooltip=["Year-Month", "count"],
    ).properties(height=320, width="container")
    st.altair_chart(chart, use_container_width=True)


def render_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = BRAND_PALETTE[1]) -> None:
    if df.empty:
        st.info(f"No data available for {title}.")
        return
    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=color).encode(
        x=alt.X(f"{y_col}:Q", title="Count"),
        y=alt.Y(f"{x_col}:N", sort="-x", title=None),
        tooltip=[x_col, y_col],
    ).properties(height=340, width="container")
    st.subheader(title)
    st.altair_chart(chart, use_container_width=True)


def render_company_table(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No company data available for the current filters.")
        return
    st.subheader("Top companies by complaint volume")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)


def render_radar_chart(df: pd.DataFrame, selected_companies: list) -> None:
    if not PLOTLY_AVAILABLE:
        st.error("Plotly is not installed in the current environment. Install plotly to view the AI Risk Radar.")
        return
    if df.empty:
        st.info("No company metrics available for the current filters.")
        return
    if not selected_companies:
        selected_companies = df["Company"].head(3).tolist()
    categories = [
        "Complaint volume",
        "Timely response risk",
        "Dispute risk",
        "Severity risk",
        "Financial impact risk",
        "Escalation risk",
    ]
    fig = go.Figure()
    for company in selected_companies:
        row = df[df["Company"] == company]
        if row.empty:
            continue
        values = [
            float(row["complaint_volume"].iloc[0]),
            float(row["timely_response_risk"].iloc[0]),
            float(row["dispute_risk"].iloc[0]),
            float(row["severity_risk"].iloc[0]),
            float(row["financial_impact_risk"].iloc[0]),
            float(row["escalation_risk"].iloc[0]),
        ]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name=company,
            )
        )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=10),
    )
    st.subheader("AI Risk Radar")
    st.plotly_chart(fig, use_container_width=True, key="company_risk_radar")


def render_heatmap(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No data available for the heatmap.")
        return

    heatmap_data = df.fillna(0).astype(int)
    max_value = int(heatmap_data.values.max()) if not heatmap_data.empty else 0

    def _annotate_cell(value: int) -> str:
        if value <= 0:
            return "0"
        intensity = min(5, max(1, round((value / max_value) * 5))) if max_value > 0 else 1
        return f"{value} {'🔥' * intensity}"

    display_data = heatmap_data.apply(lambda column: column.map(_annotate_cell))
    st.subheader("Product vs Issue heatmap")
    st.markdown("Color intensity and emoji count represent complaint volume for each product / issue pair.")
    st.dataframe(display_data, use_container_width=True)


def render_ai_agent_stat_cards(risk_result: dict, trend_result: dict, consumer_result: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"### Consumer Safety Index\n**{consumer_result.get('safety_index', 0.0):.0f}%**")
    col2.markdown(f"### Top Emerging Risk\n**{', '.join(trend_result.get('top_emerging_risks', [])[:1]) or 'N/A'}**")
    col3.markdown(f"### Highest Risk Company\n**{risk_result.get('highest_risk_company', 'N/A')}**")
    col4.markdown(f"### Risk Level\n**{risk_result.get('risk_level', 'Unknown')}**")


def render_ai_agent_flow() -> None:
    st.markdown(
        "#### Agent collaboration flow"
        "\n"
        "Data → Risk Agent → Trend Agent → Consumer Impact Agent → Executive Agent"
    )
    st.caption("A deterministic, rule-based intelligence flow that turns complaint patterns into analyst-ready briefing points.")


def render_ai_command_center(
    risk_result: dict,
    trend_result: dict,
    consumer_result: dict,
    executive_result: dict,
    briefing_markdown: str,
) -> None:
    st.subheader("AI Command Center")
    render_ai_agent_flow()
    render_ai_agent_stat_cards(risk_result, trend_result, consumer_result)
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Risk Agent")
        st.markdown(f"**Highest-risk company:** {risk_result.get('highest_risk_company', 'N/A')}  ")
        st.markdown(f"**Top risk drivers:** {', '.join(risk_result.get('top_risk_drivers', [])) or 'N/A'}  ")
        st.markdown(f"{risk_result.get('risk_message', '')}")

        st.markdown("### Trend Agent")
        st.markdown(f"**Trend direction:** {trend_result.get('trend_direction', 'N/A')}  ")
        st.markdown(f"**Recent change:** {trend_result.get('percentage_change', 0.0):.1f}%  ")
        st.markdown(f"{trend_result.get('trend_message', '')}")

    with col2:
        st.markdown("### Consumer Impact Agent")
        st.markdown(f"**Watch items:** {', '.join(consumer_result.get('watch_items', [])) or 'N/A'}  ")
        st.markdown(f"**Warning signs:** {', '.join(consumer_result.get('warning_signs', []))}")
        st.markdown(f"**Recommended actions:** {', '.join(consumer_result.get('recommendations', []))}")

    st.markdown("---")
    st.markdown("### Executive Agent briefing")
    st.markdown(f"**Confidence level:** {executive_result.get('confidence_level', 'Moderate')}  ")
    for bullet in executive_result.get('summary_bullets', []):
        st.markdown(f"- {bullet}")

    if briefing_markdown:
        st.download_button(
            label="Download AI briefing",
            data=briefing_markdown.encode('utf-8'),
            file_name="ai_command_center_briefing.md",
            mime="text/markdown",
            key="download_ai_briefing",
        )


def render_state_map(df: pd.DataFrame) -> None:
    if not PLOTLY_AVAILABLE:
        st.error("Plotly is not installed in the current environment. Install plotly to view the US state map.")
        return
    if df.empty:
        st.info("No state intelligence available for the current filters.")
        return
    map_df = df.copy()
    map_df["State Code"] = map_df["State"].apply(state_to_plotly_location)
    map_df = map_df.dropna(subset=["State Code"])
    if map_df.empty:
        st.info("No mappable U.S. state codes are available for the current filters.")
        return
    fig = px.choropleth(
        map_df,
        locations="State Code",
        locationmode="USA-states",
        color="risk_score",
        scope="usa",
        hover_data={
            "State": True,
            "complaints": True,
            "dispute_rate": ":.1f",
            "timely_rate": ":.1f",
            "risk_label": True,
            "State Code": False,
        },
        color_continuous_scale="Reds",
        labels={"risk_score": "State risk"},
    )
    fig.update_layout(title_text="US Complaint Intelligence Map", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True, key="state_map")


def format_scorecard_html(card: dict) -> str:
    company = escape(str(card.get("Company", "Unknown")))
    risk_label = escape(str(card.get("risk_label", "Unknown")))
    trend = escape(str(card.get("trend_direction", "Stable")))
    top_drivers = ", ".join(escape(str(driver)) for driver in card.get("top_drivers", []))
    overall_risk = float(card.get("overall_risk", 0.0))
    return (
        "<div class='section-card'>"
        f"<div class='card-title'>{company}</div>"
        f"<div class='card-value'>{overall_risk:.1f}</div>"
        f"<div>{risk_label}</div>"
        f"<div>Top drivers: {top_drivers}</div>"
        f"<div>Trend: {trend}</div>"
        "</div>"
    )


def render_scorecards(cards: list) -> None:
    if not cards:
        st.info("No scorecards available for the selected companies.")
        return
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        col.markdown(format_scorecard_html(card), unsafe_allow_html=True)


def render_forecast_plot(history: pd.DataFrame, forecast: pd.DataFrame, title: str) -> None:
    if not PLOTLY_AVAILABLE:
        st.error("Plotly is not installed in the current environment. Install plotly to view the forecast chart.")
        return
    if history.empty:
        st.info("No historical data available for forecasting.")
        return
    if forecast.empty:
        st.warning("Not enough historical data for a reliable forecast.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name="History",
            x=history["Date received"],
            y=history["count"],
            mode="lines+markers",
            marker=dict(size=6),
            line=dict(color="#0f4c81", width=3),
            hovertemplate="Month: %{x|%Y-%m}<br>Complaints: %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Forecast",
            x=forecast["Date received"],
            y=forecast["forecast"],
            mode="lines+markers",
            marker=dict(size=6),
            line=dict(color="#f26419", dash="dash", width=3),
            hovertemplate="Month: %{x|%Y-%m}<br>Forecast: %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Confidence Range",
            x=list(forecast["Date received"]) + list(forecast["Date received"][::-1]),
            y=list(forecast["upper"]) + list(forecast["lower"][::-1]),
            fill="toself",
            fillcolor="rgba(246, 100, 25, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        title=title,
        yaxis_title="Monthly complaints",
        xaxis_title="Month",
        yaxis=dict(tickformat=",d"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=520,
        margin=dict(t=40, b=40, l=60, r=20),
    )
    st.plotly_chart(fig, use_container_width=True, key="forecast_plot")


def render_ask_results(summary: str, chart: Optional[dict]) -> None:
    st.markdown("#### Ask the Data")
    st.markdown(summary)
    if not PLOTLY_AVAILABLE:
        if chart and chart.get("data") is not None:
            st.info("The query returned data, but Plotly is not installed so charts cannot be rendered.")
        return
    if chart and chart.get("data") is not None:
        if chart["type"] == "bar":
            fig = px.bar(chart["data"], x=chart["x"], y=chart["y"], title=chart.get("title", "Query result"))
            st.plotly_chart(fig, use_container_width=True, key=f"ask_result_{chart.get('title', 'query')}")


def render_executive_summary(summaries: list) -> None:
    st.subheader("Executive summary")
    for sentence in summaries:
        st.markdown(f"- {sentence}")


def render_insights(insights: list) -> None:
    st.subheader("Rule-based insights")
    for insight in insights:
        st.markdown(f"- {insight}")


def render_consumer_guidance() -> None:
    st.header("Consumer guidance")
    st.markdown(
        """
        Consumer Finance Complaint Radar is designed to help you see patterns quickly using the left sidebar filters.

        **How to use the dashboard**
        - Start with the date range and product filter in the sidebar to focus your review.
        - Drill into top companies and issues to compare providers.
        - Use the risk signals to identify elevated complaint areas.

        **Why this matters**
        - Consumers can compare complaints across banks, cards, mortgages, loans, and payment services.
        - High dispute and low timely response rates can signal chronic service issues.
        - This tool is built for transparency, not to replace professional advice.

        **If you need to take action**
        1. Document the problem clearly and keep all correspondence.
        2. Contact the company directly and ask for remediation.
        3. File a CFPB complaint if the issue remains unresolved.

        **Helpful resources**
        - CFPB complaint portal: https://www.consumerfinance.gov/complaint/
        - Learn more about your rights for credit cards, mortgages, and loans.
        """
    )
