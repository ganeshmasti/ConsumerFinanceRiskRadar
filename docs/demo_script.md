# Demo Script: AI Command Center

## Key talking points

- "This app now includes an AI Command Center tab that turns filtered complaint data into deterministic analyst-style intelligence."
- "It uses four rule-based agents to surface risk, trend, consumer, and executive insights without needing any external AI API."
- "The interface is designed to feel premium and executive-ready, with a safety score, emerging risk signal, highest-risk company, and briefing download."

## Presentation flow

1. Start on the Dashboard tab and show the sidebar validation messages for the offline sample dataset.
2. Point out the KPI cards, trend chart, forecast, product chart, state chart, issue chart, and heatmap.
3. Open Company Comparison and compare Experian, Equifax, and TransUnion using the risk radar and scorecards.
4. Open Guidance and ask: `how is experian compared with equifax?`
5. Open the `AI Command Center` tab after filtering the dataset.
6. Click `Generate AI Briefing` to run the rule-based agent pipeline.
7. Highlight the summary cards: Consumer Safety Index, Top Emerging Risk, Highest Risk Company, and Risk Level.
8. Review the Risk Agent, Trend Agent, Consumer Impact Agent, and Executive Agent outputs.
9. Download the briefing as markdown and explain that it is a self-contained, offline-ready intelligence summary.

## Why this matters

- It turns raw complaint counts into actionable risk signals.
- It supports executive storytelling with a clear analytics flow.
- It keeps the experience fully demo-ready without API keys or paid models.

## Backup Plan
- If an upload fails during the demo, use the bundled sample dataset and point to the sidebar validation message.
- If filters produce no data, clear company/state/issue filters and reset the date range.
- If forecasting shows insufficient history, widen the date range to include at least six months.
- If asked about AI, explain that the current version is deterministic and offline for repeatable demos.

## Closing Line
"Consumer Finance Complaint Radar turns complaint data into an explainable, filter-aware risk story that a consumer advocate, founder, or analyst can demonstrate without live APIs or secrets."
