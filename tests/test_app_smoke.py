import os

from src.data_loader import load_sample_data
from streamlit_app import transform_complaint_data_cached


def test_streamlit_app_cached_transform_accepts_sample_data():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    raw_df = load_sample_data(path)

    transformed = transform_complaint_data_cached(raw_df)

    assert not transformed.empty
    assert {"Year", "Year-Month", "Quarter", "Company type"}.issubset(transformed.columns)
