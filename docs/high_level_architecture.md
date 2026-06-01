# High-Level System Architecture - Consumer Finance Risk Radar

This document provides a business/product-level architecture view of Consumer Finance Risk Radar. It is designed for Week 1 project documentation, GitHub, Mermaid Live Editor, and presentation exports.

## Diagram

```mermaid
flowchart TB
    subgraph sources["1. Data Sources"]
        dataset["CFPB-style 25K Complaint Dataset"]
        upload["Optional User CSV Upload"]
    end

    subgraph ingestion["2. Data Ingestion Layer"]
        csv_loader["CSV Loader"]
        schema_validation["Schema Validation"]
        quality_checks["Data Quality Checks"]
    end

    subgraph processing["3. Data Processing Layer"]
        cleaning["Cleaning"]
        transformation["Transformation"]
        features["Feature Engineering"]
        timeseries["Time-Series Preparation"]
    end

    subgraph intelligence["4. Intelligence Layer"]
        analytics["Analytics Engine"]
        risk_scoring["Risk Scoring Engine"]
        forecasting["Forecasting Engine"]
        safety_index["Consumer Safety Index"]
        ai_insights["AI Insights Engine"]
    end

    subgraph agentic["5. Agentic AI Layer"]
        risk_agent["Risk Agent"]
        trend_agent["Trend Agent"]
        consumer_agent["Consumer Impact Agent"]
        executive_agent["Executive Agent"]
        ask_data["Ask-the-Data Assistant"]
    end

    subgraph presentation["6. Presentation Layer"]
        dashboard["Streamlit Dashboard"]
        kpis["KPI Cards"]
        charts["Charts"]
        maps["Maps"]
        radar["Risk Radar"]
        command_center["AI Command Center"]
        reports["Downloadable Reports"]
    end

    subgraph users["7. End Users"]
        consumers["Consumers"]
        analysts["Analysts"]
        advocates["Advocates"]
        reviewers["Bootcamp Reviewers"]
    end

    dataset --> csv_loader
    upload --> csv_loader
    csv_loader --> schema_validation
    schema_validation --> quality_checks
    quality_checks --> cleaning
    cleaning --> transformation
    transformation --> features
    features --> timeseries

    timeseries --> analytics
    timeseries --> risk_scoring
    timeseries --> forecasting
    risk_scoring --> safety_index
    analytics --> ai_insights
    forecasting --> ai_insights
    safety_index --> ai_insights

    risk_scoring --> risk_agent
    forecasting --> trend_agent
    safety_index --> consumer_agent
    ai_insights --> ask_data
    risk_agent --> trend_agent
    trend_agent --> consumer_agent
    consumer_agent --> executive_agent

    analytics --> dashboard
    risk_scoring --> radar
    forecasting --> charts
    safety_index --> kpis
    ai_insights --> dashboard
    risk_agent --> command_center
    trend_agent --> command_center
    consumer_agent --> command_center
    executive_agent --> command_center
    ask_data --> dashboard

    dashboard --> kpis
    dashboard --> charts
    dashboard --> maps
    dashboard --> radar
    command_center --> reports
    dashboard --> reports

    kpis --> consumers
    charts --> analysts
    maps --> advocates
    radar --> analysts
    command_center --> reviewers
    reports --> consumers
    reports --> analysts
    reports --> advocates
    reports --> reviewers
```

## Short Explanation

This architecture shows Consumer Finance Risk Radar as a layered intelligence platform. Complaint data enters through either the bundled CFPB-style sample dataset or an optional user upload. The data is validated, cleaned, transformed, and prepared for analytics. The intelligence layer produces risk scores, forecasts, Consumer Safety Index signals, and rule-based insights. The agentic AI layer turns those signals into risk, trend, consumer impact, executive, and natural-language assistant outputs. The Streamlit presentation layer converts the analysis into dashboard views, KPI cards, charts, maps, risk radar, AI Command Center briefings, and downloadable reports for consumers, analysts, advocates, and bootcamp reviewers.

## Google Doc Paragraph

Consumer Finance Risk Radar is organized as a layered consumer-risk intelligence platform. CFPB-style complaint data flows through ingestion, validation, cleaning, transformation, and time-series preparation before reaching the intelligence layer, where the system calculates analytics, risk scores, forecasts, Consumer Safety Index signals, and AI-generated insights. A deterministic agentic AI layer then converts those signals into Risk Agent, Trend Agent, Consumer Impact Agent, Executive Agent, and Ask-the-Data Assistant outputs. Finally, the Streamlit presentation layer delivers KPI cards, charts, maps, risk radar, an AI Command Center, and downloadable reports for consumers, analysts, advocates, and bootcamp reviewers.

## How to Render in Mermaid Live Editor

1. Open [Mermaid Live Editor](https://mermaid.live/).
2. Copy only the Mermaid code block from the **Diagram** section above.
3. Paste it into the editor panel.
4. Choose a clean theme such as `default`, `base`, or `neutral`.
5. Export as PNG or SVG for your Week 1 submission, README assets, or presentation slides.

