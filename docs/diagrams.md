# Consumer Finance Risk Radar Architecture Diagrams

Professional Mermaid diagrams for the Consumer Finance Risk Radar project documentation, GitHub README, Mermaid Live Editor, Draw.io, Excalidraw, and Lucidchart workflows.

## Implementation Mapping

The requested architecture names `risk_scoring.py` and `visualizations.py` as conceptual components. In the current codebase, those responsibilities are implemented as:

- Risk scoring: `src/analytics.py` for risk radar, state risk, scorecards, and forecasting inputs; `src/agents.py` for AI Command Center risk scoring.
- Visualizations: `src/ui.py` for charts, maps, radar chart, scorecards, filters, downloads, and Streamlit UI rendering.

## 1. Solution Architecture Diagram

### Description
This diagram shows the end-to-end platform architecture from the bundled CFPB-style 25K complaint dataset and optional CSV upload through validation, transformation, analytics, AI insights, and Streamlit presentation.

### Business Purpose
It communicates that Consumer Finance Risk Radar is not just a dashboard; it is a complete consumer-risk intelligence pipeline that turns raw complaints into explainable metrics, forecasts, AI briefings, and user-facing decision support.

### Technical Explanation
`streamlit_app.py` orchestrates the workflow. `src/data_loader.py` reads and validates data, `src/transform.py` standardizes fields, `src/analytics.py` computes metrics and forecasts, `src/insights.py` generates narrative insights, `src/agents.py` powers the multi-agent command center, `src/assistant.py` answers natural-language questions, and `src/ui.py` renders the Streamlit experience.

### Mermaid

```mermaid
flowchart TB
    user["User / Reviewer"]
    sample["CFPB-style 25K Complaint Dataset<br/>sample_data/cfpb_complaints_sample.csv"]
    upload["Optional User CSV / TSV Upload"]

    app["Streamlit Dashboard<br/>streamlit_app.py"]
    loader["Data Loader Layer<br/>src/data_loader.py"]
    validation["Data Validation Layer<br/>file type, size, schema, dates, empty rows,<br/>formula-injection neutralization"]
    transform["Data Transformation Layer<br/>src/transform.py<br/>product, state, company type, time buckets"]

    analytics["Analytics Engine<br/>src/analytics.py<br/>KPIs, products, issues, states, company summaries"]
    risk["Risk Scoring Engine<br/>analytics.py + agents.py<br/>company risk, state risk, escalation risk"]
    forecast["Forecasting Engine<br/>forecast_complaint_volume()<br/>monthly trend + confidence range"]
    safety["Consumer Safety Index<br/>analyze_consumer_agent()"]
    insights["AI Insights Engine<br/>src/insights.py<br/>rule-based narratives"]
    agents["Multi-Agent AI Command Center<br/>src/agents.py"]
    assistant["Ask-the-Data Assistant<br/>src/assistant.py"]
    ui["Visualization and Interaction Layer<br/>src/ui.py<br/>charts, filters, maps, radar, scorecards, downloads"]

    user --> app
    sample --> loader
    upload --> loader
    app --> loader
    loader --> validation
    validation --> transform
    transform --> analytics
    transform --> insights
    transform --> agents
    transform --> assistant

    analytics --> risk
    analytics --> forecast
    agents --> safety
    agents --> risk
    risk --> ui
    forecast --> ui
    safety --> ui
    insights --> ui
    agents --> ui
    assistant --> ui
    ui --> app
    app --> user
```

## 2. Multi-Agent AI Workflow Diagram

### Description
This diagram shows the deterministic multi-agent analysis sequence used by the AI Command Center.

### Business Purpose
It helps judges and recruiters understand how the platform turns filtered complaints into an executive-ready briefing without external API keys or non-deterministic model calls.

### Technical Explanation
The command center uses functions in `src/agents.py`. The app runs the Risk Agent, then Trend Agent, then Consumer Impact Agent, then Executive Agent. The briefing is created by `build_briefing_markdown()`.

### Mermaid

```mermaid
flowchart TB
    dataset["Complaint Dataset<br/>filtered pandas DataFrame"]

    risk["Risk Agent<br/>Purpose: identify highest-risk companies and drivers<br/>Inputs: filtered complaints, dispute flags, timely response, severity, financial impact<br/>Outputs: highest-risk company, risk level, risk table, risk message"]

    trend["Trend Agent<br/>Purpose: detect emerging complaint patterns<br/>Inputs: filtered complaints, Year-Month, Year, Product, Issue, State<br/>Outputs: trend direction, percentage change, emerging risks, spike details"]

    consumer["Consumer Impact Agent<br/>Purpose: translate risk into consumer-facing guidance<br/>Inputs: filtered complaints, Risk Agent output, Trend Agent output<br/>Outputs: Consumer Safety Index, watch items, warning signs, recommendations"]

    executive["Executive Agent<br/>Purpose: synthesize board-level findings<br/>Inputs: Risk, Trend, and Consumer Impact outputs<br/>Outputs: top findings, key risks, recommended actions, confidence level"]

    briefing["Executive Briefing<br/>downloadable markdown report"]

    dataset --> risk
    risk --> trend
    trend --> consumer
    consumer --> executive
    executive --> briefing
```

## 3. Component Interaction Diagram

### Description
This diagram maps the actual Python files and how they interact inside the Streamlit application.

### Business Purpose
It gives reviewers a fast technical overview of project structure and maintainability.

### Technical Explanation
The app is intentionally modular. The entrypoint coordinates loading, transformation, filtering, analytics, assistant responses, agent workflows, and UI rendering. There are no separate `risk_scoring.py` or `visualizations.py` files; those responsibilities are implemented in `analytics.py`, `agents.py`, and `ui.py`.

### Mermaid

```mermaid
flowchart LR
    app["streamlit_app.py<br/>entrypoint and orchestration"]
    constants["constants.py<br/>schema, labels, risk weights, templates"]
    loader["data_loader.py<br/>load sample/uploaded data<br/>validate schema and quality"]
    transform["transform.py<br/>normalize products, states, company types, time fields"]
    analytics["analytics.py<br/>KPIs, scorecards, risk radar, state risk, forecasting, heatmaps"]
    insights["insights.py<br/>rule-based insight narratives"]
    agents["agents.py<br/>Risk, Trend, Consumer Impact, Executive agents"]
    assistant["assistant.py<br/>Ask-the-Data responses and executive summary"]
    ui["ui.py<br/>filters, charts, maps, radar, scorecards, downloads"]
    sample["sample_data/cfpb_complaints_sample.csv"]
    tests["tests/<br/>unit and smoke coverage"]

    app --> loader
    app --> transform
    app --> analytics
    app --> insights
    app --> agents
    app --> assistant
    app --> ui

    loader --> constants
    transform --> constants
    analytics --> constants
    insights --> constants
    assistant --> constants
    agents --> constants
    ui --> constants

    sample --> loader
    insights --> analytics
    assistant --> analytics
    ui --> analytics
    tests --> loader
    tests --> transform
    tests --> analytics
    tests --> assistant
    tests --> ui
    tests --> app
```

## 4. User Workflow Diagram

### Description
This diagram shows the user journey from opening the app to exporting insights.

### Business Purpose
It frames the project as a practical workflow for analysts, founders, consumer advocates, and demo reviewers.

### Technical Explanation
Users can start with the sample dataset or upload a validated CSV/TSV. Filters drive all downstream tabs. Analytics, AI insights, command-center outputs, assistant responses, and downloads all operate on the current filtered dataset.

### Mermaid

```mermaid
flowchart TB
    user["User"]
    start["Open Streamlit App"]
    data["Upload CSV / TSV<br/>or Load Sample Dataset"]
    validate["Validate Dataset<br/>schema, file size, dates, required fields"]
    filters["Apply Filters<br/>date, year, product, state, company, issue"]
    analytics["View Analytics<br/>KPIs, trends, forecast, product/state/issue charts, heatmap"]
    company["Compare Companies<br/>summary table, risk radar, scorecards"]
    insights["Generate AI Insights<br/>rule-based insights and executive summary"]
    command["Run AI Command Center<br/>Risk, Trend, Consumer Impact, Executive agents"]
    ask["Ask-the-Data Assistant<br/>natural-language analytical questions"]
    download["Download Report / Filtered Data<br/>CSV and markdown briefing"]

    user --> start
    start --> data
    data --> validate
    validate --> filters
    filters --> analytics
    filters --> company
    filters --> insights
    filters --> command
    filters --> ask
    analytics --> download
    company --> download
    insights --> download
    command --> download
    ask --> download
```

## PNG-Ready Rendering

Each Mermaid block above can be rendered directly as PNG or SVG using:

- GitHub Markdown preview
- Mermaid Live Editor
- Draw.io Mermaid import
- Lucidchart Mermaid import
- Excalidraw Mermaid-to-Excalidraw workflows

Recommended export settings:

- Format: PNG for submissions, SVG for crisp README/docs rendering
- Theme: default or neutral
- Background: white
- Width: 1600 px or higher for slide decks

## Recommended Diagrams for Week 1 Submission

Use these two diagrams for the strongest first impression:

1. **Solution Architecture Diagram**: best for judges because it shows the full system, data flow, AI features, and technical maturity in one view.
2. **Multi-Agent AI Workflow Diagram**: best for recruiters because it clearly explains the AI Command Center and makes the project feel differentiated, deterministic, and demo-ready.

