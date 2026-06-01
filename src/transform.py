import pandas as pd

from src.constants import (
    FINTECH_KEYWORDS,
    PRODUCT_CATEGORIES,
    STATE_ABBREVIATIONS,
    TRADITIONAL_KEYWORDS,
)


def normalize_product(product: str) -> str:
    if not isinstance(product, str):
        return "Other financial service"
    product = product.strip()
    if product in PRODUCT_CATEGORIES:
        return product
    lowered = product.lower()
    if "credit" in lowered and "card" in lowered:
        return "Credit card"
    if "mortgage" in lowered:
        return "Mortgage"
    if "loan" in lowered:
        return "Consumer loan"
    if "money" in lowered or "payment" in lowered or "currency" in lowered:
        return "Money transfer, virtual currency, or payment"
    if "bank" in lowered or "account" in lowered:
        return "Bank account or service"
    return "Other financial service"


def normalize_state(state: str) -> str:
    if not isinstance(state, str):
        return "Unknown"
    code = state.strip().upper()
    return STATE_ABBREVIATIONS.get(code, state.title())


def infer_company_type(company: str) -> str:
    if not isinstance(company, str) or not company.strip():
        return "Other"
    lowered = company.lower()
    if any(term in lowered for term in FINTECH_KEYWORDS) and not any(term in lowered for term in ["bank", "mortgage", "trust"]):
        return "Fintech-style"
    if any(term in lowered for term in TRADITIONAL_KEYWORDS):
        return "Traditional"
    return "Other"


def derive_time_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Year"] = df["Date received"].dt.year
    df["Month"] = df["Date received"].dt.month
    df["Year-Month"] = df["Date received"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Date received"].dt.to_period("Q").astype(str)
    return df


def transform_complaint_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Product"] = df["Product"].fillna("Other financial service").map(normalize_product)
    df["State"] = df["State"].fillna("Unknown").map(normalize_state)
    df["Issue"] = df["Issue"].fillna("Other")
    df["Timely response?"] = df["Timely response?"].astype(str).str.title()
    df["Consumer disputed?"] = df["Consumer disputed?"] .astype(str).str.title()
    df["Company type"] = df["Company"].fillna("Unknown").apply(infer_company_type)
    df = derive_time_fields(df)
    return df
