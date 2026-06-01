# Consumer Finance Complaint Radar User Guide

## What this app shows
- complaint volume and trends across U.S. financial products
- ranked top products, issues, states, and companies
- company comparison analytics with fintech-style versus traditional providers
- filter and export functionality for clean dataset review
- consumer guidance and complaint filing recommendations

## How to use it
1. Upload a CFPB-style CSV or use the offline sample dataset.
2. Adjust the date range and product selection in the sidebar.
3. Refine by state and issue to focus on the most relevant complaints.
4. Use the tabs to switch between the overall dashboard, company comparison, guidance, and the new AI Command Center.
5. Visit the AI Command Center, generate the briefing, and download the markdown summary for executive review.
6. Export filtered results with the Download button.

## Enhanced validation
- The sidebar displays dataset validation messages and warnings.
- Missing or invalid fields are surfaced before you proceed.
- Uploads must be CSV or TSV files under 20 MB.
- Rows with invalid complaint dates are removed because date filters, trends, and forecasts require valid dates.

## Notes
- The dataset schema is fixed to the sample format for this MVP.
- Company types are inferred heuristically to support fintech-style comparison.
- This app is designed for entrepreneur-grade presentation and can be extended to real CFPB uploads.

## Ask the Data Examples
- Which companies have the highest fraud risk?
- How is Experian compared with Equifax?
- What is the most frequent issue?
- Which state has the most complaints?
- Which product grew the most in 2025?

## Troubleshooting
- If filters return no rows, clear state/company/issue filters or widen the date range.
- If the AI Command Center says the dataset is small, widen filters before generating a briefing.
- If forecasting is unavailable, select a range with at least six months of complaint history.
- If an upload fails, check that all required CFPB-style columns are present.
- If the state map does not color a row, confirm that `State` contains a U.S. state name or two-letter code.

## Interpreting Scores
- Higher complaint volume means more records in the selected view, not necessarily a larger market-adjusted risk.
- Dispute and untimely response rates are percentages of filtered complaints.
- Overall risk is a heuristic score for comparison inside the current filtered dataset.
- Forecasts are directional demo estimates and should not be treated as financial, legal, or regulatory advice.
