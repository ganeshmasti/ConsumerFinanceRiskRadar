# Consumer Finance Complaint Radar Architecture

## Overview
This app is a single-page Streamlit application that loads an offline sample CFPB-style complaint dataset, applies rule-based analytics, and renders interactive charts, company comparisons, and consumer guidance.

## Components
- `streamlit_app.py`: application entrypoint, branding, tab navigation, and content orchestration
- `src/data_loader.py`: CSV loading, schema validation, and upload feedback
- `src/transform.py`: data normalization, company type inference, and time bucket creation
- `src/analytics.py`: aggregate metrics, company summary, and complaint breakdowns
- `src/insights.py`: narrative insight generation and signals
- `src/ui.py`: branding, filter panel, charts, validation UI, and download helpers
- `sample_data/cfpb_complaints_sample.csv`: offline sample dataset with representative complaint cases
- `assets/logo.svg`: brand logo for the app header

## Data flow
1. Load sample or uploaded CSV
2. Validate required schema and data quality
3. Normalize products, states, and company types
4. Apply filters
5. Compute overview metrics, company comparison analytics, and charts
6. Generate insights and render consumer guidance
7. Allow users to export filtered complaint data

## Architecture Diagram Description
User input enters through Streamlit's sidebar as either the bundled sample dataset or a validated upload. The data loader enforces file size, file type, schema, date validity, and spreadsheet-formula neutralization. The transform layer normalizes products, states, company types, and time buckets. Filtered data then fans out into analytics, insights, the Ask-the-Data assistant, and the AI Command Center. The UI layer renders charts, scorecards, maps, downloads, and validation messages without external network calls.

## Analytics Model
- KPI cards use direct counts and modal values from the filtered dataset.
- Company summaries aggregate complaint volume, dispute rate, timely response rate, and inferred company type.
- Risk radar scores combine normalized complaint volume, timely-response risk, dispute risk, product impact, issue severity, and escalation risk.
- State risk combines normalized complaint volume, dispute rate, timely-response risk, and issue severity.
- Forecasting groups actual complaints by month-end and projects six months using a simple linear trend with residual-based confidence bands.
- AI agents are deterministic functions that summarize risk, trend, consumer impact, and executive briefing outputs from the filtered data.

## Reliability Boundaries
- Empty datasets return explicit no-data messages.
- Forecasting returns structured statuses: `no_data`, `not_enough_history`, or `ok`.
- Uploaded files are rejected before analysis if they are too large, malformed, empty, or missing required columns.
- The application does not evaluate uploaded content as code and does not execute shell commands.

## Security Notes
- No API keys or credentials are required.
- Dynamic scorecard HTML escapes uploaded company, issue, and label content.
- `.streamlit/secrets.toml` and environment files are ignored by `.gitignore`.
- Uploaded spreadsheet formula strings are prefixed to reduce CSV formula-injection risk on export.

## Future Architecture Options
- Add a repository/service layer if live CFPB API ingestion is introduced.
- Add browser smoke tests with Playwright or Streamlit's testing utilities.
- Replace linear forecasting with a model registry only if forecasting becomes a core product feature.
- Persist generated briefings only after adding storage controls and data-retention policy.
