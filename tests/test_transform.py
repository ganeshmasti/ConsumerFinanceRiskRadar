import os

import pandas as pd

from src.data_loader import load_sample_data
from src.transform import transform_complaint_data


def test_transform_normalizes_product_state_and_infers_company_type():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    df = load_sample_data(path)
    transformed = transform_complaint_data(df)
    assert "Year" in transformed.columns
    assert "Quarter" in transformed.columns
    assert "Company type" in transformed.columns
    assert transformed["Product"].isin([
        "Bank account or service",
        "Credit card",
        "Mortgage",
        "Consumer loan",
        "Money transfer, virtual currency, or payment",
        "Other financial service",
    ]).all()
    assert transformed["State"].str.len().gt(0).all()
    assert transformed["Company type"].isin(["Traditional", "Fintech-style", "Other"]).all()
