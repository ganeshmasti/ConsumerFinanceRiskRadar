APP_NAME = "Consumer Finance Complaint Radar"
APP_TAGLINE = "A public-good dashboard for U.S. consumer complaint patterns across banking, credit, mortgage, and fintech flows."
APP_DESCRIPTION = (
    "Explore complaint trends, top issues, company insights, and consumer guidance with a polished offline demo dataset."
)

PRODUCT_CATEGORIES = [
    "Bank account or service",
    "Credit card",
    "Mortgage",
    "Consumer loan",
    "Money transfer, virtual currency, or payment",
    "Other financial service",
]

REQUIRED_COLUMNS = [
    "Date received",
    "Product",
    "Sub-product",
    "Issue",
    "Sub-issue",
    "Company",
    "State",
    "ZIP code",
    "Submitted via",
    "Company response",
    "Timely response?",
    "Consumer disputed?",
    "Complaint ID",
]

STATE_ABBREVIATIONS = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
    'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
    'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
    'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
    'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia',
}

FINTECH_KEYWORDS = [
    "pay",
    "wallet",
    "crypto",
    "lend",
    "lending",
    "neo",
    "virtual",
    "digital",
    "mobile",
    "transfer",
    "fin",
    "capital",
]

TRADITIONAL_KEYWORDS = [
    "bank",
    "mortgage",
    "credit union",
    "savings",
    "trust",
    "national",
    "association",
    "federal",
]

BRAND_PALETTE = ["#0f4c81", "#2a9d8f", "#f4a261", "#e76f51", "#264653"]

ISSUE_SEVERITY = {
    "Billing disputes": 0.9,
    "Loan servicing": 0.7,
    "Account opening": 0.5,
    "Collection debt problem": 0.95,
    "Money was not received": 0.85,
    "Problem with a purchase": 0.75,
    "Loan payment": 0.8,
    "Managing an account": 0.65,
    "Payment option problems": 0.7,
    "Fraud": 1.0,
    "Credit reporting": 0.8,
    "Identity theft": 1.0,
    "Billing statement": 0.6,
    "Customer service": 0.5,
    "Account closing": 0.9,
    "Transaction problem": 0.85,
    "Escrow account": 0.9,
    "Dispute process": 0.9,
    "Withdrawal problem": 0.8,
    "Debt was sold or transferred": 0.9,
    "Incorrect information on report": 0.85,
    "Loan terms": 0.75,
}

PRODUCT_IMPACT = {
    "Credit card": 0.9,
    "Mortgage": 0.8,
    "Consumer loan": 0.85,
    "Bank account or service": 0.7,
    "Money transfer, virtual currency, or payment": 0.95,
    "Other financial service": 0.65,
}

AI_SUMMARY_TEMPLATES = {
    "major_trends": "The filtered set shows {top_state} and {top_product} as leading complaint drivers, with {top_issue} as the most prominent issue.",
    "unusual_spike": "A sharper-than-normal increase in {issue_or_state} suggests an emerging problem in the current view.",
    "high_risk_institutions": "{company_list} stand out as the highest risk institutions, driven by elevated dispute and response risks.",
    "consumer_implications": "Consumers should be cautious about {risk_theme}, as these patterns can signal systemic service or compliance gaps.",
}

INSIGHT_TEMPLATES = {
    "top_product": "The most complained-about product is {product} with {count} complaints.",
    "top_issue": "The top issue reported is {issue}, accounting for {pct:.1f}% of filtered complaints.",
    "top_state": "{state} has the highest complaint volume in the selected view.",
    "rising_product": "{product} showed the fastest recent growth, up {growth:.1f}% compared to the prior period.",
    "dispute_rate": "{product} has the highest dispute rate at {pct:.1f}% in the selected data.",
}
