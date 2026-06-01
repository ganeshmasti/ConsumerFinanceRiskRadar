import os
import warnings

from src.analytics import aggregate_overview, company_summary, forecast_complaint_volume
from src.data_loader import load_sample_data
from src.transform import transform_complaint_data


def test_aggregate_overview_returns_expected_keys():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    df = transform_complaint_data(load_sample_data(path))
    metrics = aggregate_overview(df)
    assert set(metrics) == {"total_complaints", "top_product", "top_issue", "top_state"}
    assert metrics["total_complaints"] > 0


def test_company_summary_includes_company_type():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    df = transform_complaint_data(load_sample_data(path))
    summary = company_summary(df)
    assert "Company" in summary.columns
    assert "complaints" in summary.columns
    assert "company_type" in summary.columns
    assert not summary.empty


def test_forecast_starts_after_latest_history_without_future_warning():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    df = transform_complaint_data(load_sample_data(path))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = forecast_complaint_volume(df)

    assert result["status"] == "ok"
    assert result["forecast"]["Date received"].min() > result["history"]["Date received"].max()
    assert not [warning for warning in caught if issubclass(warning.category, FutureWarning)]
