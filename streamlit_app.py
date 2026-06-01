import os

import pandas as pd
import streamlit as st

from src.analytics import (
    aggregate_overview,
    company_risk_radar,
    company_scorecard,
    company_summary,
    complaints_by_issue,
    complaints_by_product,
    complaints_by_state,
    company_type_breakdown,
    forecast_complaint_volume,
    heatmap_product_issue,
    state_risk_summary,
    time_series,
)
from src.agents import (
    analyze_consumer_agent,
    analyze_risk_agent,
    analyze_trend_agent,
    build_briefing_markdown,
    synthesize_executive_agent,
)
from src.constants import APP_NAME
from src.data_loader import load_data
from src.insights import build_insights
from src.transform import transform_complaint_data
from src.assistant import answer_question, build_executive_summary
from src.ui import (
    filter_data,
    inject_styles,
    render_ask_results,
    render_bar_chart,
    render_brand_header,
    render_company_table,
    render_consumer_guidance,
    render_dataset_summary,
    render_download_button,
    render_executive_summary,
    render_filter_summary,
    render_filters,
    render_heatmap,
    render_insights,
    render_overview_cards,
    render_radar_chart,
    render_scorecards,
    render_state_map,
    render_time_series,
    render_forecast_plot,
    render_ai_command_center,
)


@st.cache_data(show_spinner=False)
def transform_complaint_data_cached(raw_df: pd.DataFrame) -> pd.DataFrame:
    return transform_complaint_data(raw_df)


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    render_brand_header()

    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "cfpb_complaints_sample.csv")
    uploaded_file = st.sidebar.file_uploader("Upload CFPB-style complaint CSV", type=["csv"])

    try:
        raw_df, validation_messages = load_data(uploaded_file, sample_path)
    except Exception as exc:
        st.sidebar.error(str(exc))
        return

    render_dataset_summary(raw_df, validation_messages)
    render_download_button(raw_df)

    df = transform_complaint_data_cached(raw_df)
    filters = render_filters(df)
    filtered_df = filter_data(df, filters)

    if filtered_df.empty:
        st.warning("No complaints match the selected filters. Try widening the date range or clearing a filter.")

    tabs = st.tabs(["Dashboard", "Company comparison", "Guidance", "AI Command Center"])

    with tabs[0]:
        render_filter_summary(filters)
        st.subheader("Snapshot")
        render_overview_cards(aggregate_overview(filtered_df))
        st.markdown("---")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Complaint trends")
            render_time_series(time_series(filtered_df))
            forecast_data = forecast_complaint_volume(filtered_df)
            with st.expander("Forecast debug details"):
                debug = forecast_data.get("debug", {})
                st.write("Min date:", debug.get("min_date"))
                st.write("Max date:", debug.get("max_date"))
                st.write("Monthly data points:", debug.get("monthly_points"))
                st.write("Last historical month:", debug.get("last_historical_month"))
                st.write("First forecast month:", debug.get("first_forecast_month"))
                st.write("Monthly complaint counts used for modeling:")
                st.dataframe(pd.DataFrame(debug.get("monthly_counts", [])))
            render_forecast_plot(
                forecast_data["history"],
                forecast_data["forecast"],
                "6-month complaint forecast",
            )
        with col2:
            render_bar_chart(complaints_by_product(filtered_df), "Product", "count", "Complaints by product")

        col3, col4 = st.columns([1, 1])
        with col3:
            render_bar_chart(complaints_by_state(filtered_df).head(10), "State", "count", "Top states by complaints")
        with col4:
            render_bar_chart(complaints_by_issue(filtered_df).head(10), "Issue", "count", "Top issues")

        st.markdown("---")
        render_heatmap(heatmap_product_issue(filtered_df))

        with st.expander("Insights"):
            render_insights(build_insights(filtered_df))

    with tabs[1]:
        st.subheader("Company and sector view")
        st.markdown(
            "Use the company dashboard to compare top complaint drivers, company-specific issues, and fintech-style vs. traditional providers."
        )
        st.markdown("---")
        render_company_table(company_summary(filtered_df))

        radar_df = company_risk_radar(filtered_df)
        if radar_df.empty:
            selected_companies = []
            st.info("No company risk metrics are available for the current filters.")
        else:
            selected_companies = st.multiselect(
                "Select companies to compare",
                options=radar_df["Company"].tolist(),
                default=radar_df["Company"].head(3).tolist(),
            )
            render_radar_chart(radar_df, selected_companies)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            render_heatmap(heatmap_product_issue(filtered_df))
        with col2:
            render_state_map(state_risk_summary(filtered_df))

        scorecard_companies = selected_companies or (radar_df["Company"].head(3).tolist() if not radar_df.empty else [])
        cards = [company_scorecard(filtered_df, company) for company in scorecard_companies]
        cards = [card for card in cards if card]
        render_scorecards(cards)

        st.markdown("---")
        render_bar_chart(company_type_breakdown(filtered_df), "Company type", "count", "Complaint share by company type")

    with tabs[2]:
        render_consumer_guidance()
        st.markdown("---")
        render_executive_summary(build_executive_summary(filtered_df, filters))

        st.markdown("---")
        st.subheader("Ask the Data")
        question = st.text_input("Ask a data question", "Which companies have the highest fraud risk?")
        if st.button("Run query"):
            answer = answer_question(filtered_df, question)
            render_ask_results(answer["summary"], answer["chart"])

        st.markdown("---")
        st.caption(
            "Data source: offline sample CFPB-style dataset. This demo is designed for entrepreneur-grade presentation and future extension to real CFPB uploads."
        )

    with tabs[3]:
        st.subheader("AI Command Center")
        st.markdown(
            "A rule-based intelligence hub for risk, trend, consumer, and executive analysis using the current filtered dataset."
        )
        st.markdown("---")

        if filtered_df.empty:
            st.warning("No data is available for AI analysis. Adjust the filters and try again.")
        else:
            if "ai_command_center" not in st.session_state:
                st.session_state.ai_command_center = {}

            if st.button("Generate AI Briefing", key="generate_ai_briefing"):
                with st.spinner("Running AI agents on filtered complaint data..."):
                    risk = analyze_risk_agent(filtered_df)
                    trend = analyze_trend_agent(filtered_df)
                    consumer = analyze_consumer_agent(filtered_df, risk, trend)
                    executive = synthesize_executive_agent(risk, trend, consumer)
                    briefing = build_briefing_markdown(risk, trend, consumer, executive)
                    st.session_state.ai_command_center = {
                        "risk": risk,
                        "trend": trend,
                        "consumer": consumer,
                        "executive": executive,
                        "briefing_markdown": briefing,
                    }

            ai_state = st.session_state.get("ai_command_center", {})
            if ai_state:
                render_ai_command_center(
                    ai_state["risk"],
                    ai_state["trend"],
                    ai_state["consumer"],
                    ai_state["executive"],
                    ai_state["briefing_markdown"],
                )
            elif len(filtered_df) < 50:
                st.info("Filtered data is small. Widen the filters for a stronger AI briefing.")


if __name__ == "__main__":
    main()
