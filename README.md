# Consumer Finance Complaint Radar

A polished Streamlit dashboard for exploring CFPB-style consumer complaint data across U.S. financial products.

## GitHub Description
Streamlit dashboard for CFPB-style consumer finance complaint analytics, company risk comparison, forecasting, and deterministic AI briefing workflows.

## What it includes
- offline sample complaint dataset for demo use
- structured UX with landing copy, tabs, and polished charts
- explicit data validation and user upload feedback
- filters for date range, product, state, and issue
- top product/state/issue metrics and trend charts
- company comparison analytics with fintech-style and traditional provider views
- AI Command Center with rule-based Risk, Trend, Consumer, and Executive agents
- download/export of filtered complaint data
- consumer guidance and actionable interpretation

## Quick start
1. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS or Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
$env:PYTHONPATH='.'; pytest
```

4. Run the app:
```bash
streamlit run streamlit_app.py
```

The app starts with the bundled offline sample dataset. Users can upload a CSV or TSV that follows the CFPB-style schema listed in `src/constants.py`.

## Folder structure
- `streamlit_app.py`: application entrypoint and page orchestration
- `sample_data/`: offline sample dataset for U.S. complaint analysis
- `src/`: modules for loading, validation, transform, analytics, insights, and UI
- `assets/`: brand assets and logo
- `tests/`: unit tests
- `docs/`: architecture and user guide

## Repository Topics
`streamlit`, `python`, `pandas`, `plotly`, `altair`, `consumer-finance`, `cfpb`, `data-visualization`, `risk-analytics`, `financial-services`, `complaint-analysis`, `dashboard`, `forecasting`, `ai-agents`, `public-interest-tech`

## Data safety
- Uploads are limited to CSV/TSV files under 20 MB.
- Required columns are validated before analysis.
- Invalid complaint dates are removed with a visible warning.
- Spreadsheet formula-like text is neutralized during upload handling.
- The AI Command Center is deterministic and does not call external APIs or require secrets.

## Troubleshooting
- If imports fail in tests, run them from the project root with `PYTHONPATH` set to `.`.
- If the state map is blank, confirm the dataset uses U.S. state names or two-letter state codes.
- If forecasting is unavailable, widen filters so at least six monthly history points remain.
- If an uploaded file fails validation, compare its headers with the required schema in `src/constants.py`.

## Known limitations
- This is an offline demo app, not a live CFPB ingestion pipeline.
- Risk scores are explainable heuristics, not regulatory findings.
- Forecasting uses a simple linear trend model and is intended for demo-level directional signals.
- Uploaded data is processed in-memory, so very large datasets should be pre-filtered before upload.
- What "Agent" Means in This Project: In the context of this project, an agent is a specialized analytical component responsible for evaluating a particular aspect of the dataset and producing focused insights. These agents collaborate to create a structured, explainable decision-support workflow that transforms raw complaint data into meaningful business and consumer intelligence. While these agents are deterministic and data-driven rather than fully autonomous, they demonstrate how agent-oriented architectures can decompose complex analytical tasks into specialized responsibilities and deliver richer insights than traditional dashboards alone.

## Roadmap
- Add live CFPB API ingestion.
- Split runtime and development dependencies.
- Add browser-level Streamlit smoke tests.
- Add richer natural-language parsing for Ask the Data.
- Add exportable audit reports for filtered views.
- Evolve the platform into a fully agentic enterprise solution by integrating LLM-powered reasoning, tool-using agents, multi-agent orchestration (LangGraph/CrewAI/OpenAI Agents), predictive risk intelligence, and autonomous monitoring to enable agents to investigate, collaborate, and deliver real-time decision support.
