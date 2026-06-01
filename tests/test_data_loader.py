import os
from io import BytesIO

import pandas as pd
import pytest

from src.data_loader import load_data, load_sample_data


def test_load_sample_data_reads_csv():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    df = load_sample_data(path)
    assert isinstance(df, pd.DataFrame)
    assert "Date received" in df.columns
    assert len(df) >= 1


def test_load_data_returns_validation_messages_for_sample():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    with open(path, "rb") as sample_file:
        df, messages = load_data(None, path)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(messages, list)
    assert "Loaded offline sample dataset." in messages[0]


def test_load_data_rejects_oversized_upload():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    upload = BytesIO(b"not,a,real,csv\n")
    upload.name = "complaints.csv"
    upload.size = 30 * 1024 * 1024

    with pytest.raises(ValueError, match="too large"):
        load_data(upload, path)


def test_load_data_drops_invalid_dates_and_warns():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    csv = (
        "Date received,Product,Sub-product,Issue,Sub-issue,Company,State,ZIP code,Submitted via,"
        "Company response,Timely response?,Consumer disputed?,Complaint ID\n"
        "not-a-date,Credit card,,Billing disputes,,Example Bank,CA,94105,Web,Closed,Yes,No,1\n"
        "2024-01-02,Credit card,,Billing disputes,,Example Bank,CA,94105,Web,Closed,Yes,No,2\n"
    )
    upload = BytesIO(csv.encode("utf-8"))
    upload.name = "complaints.csv"
    upload.size = len(csv)

    df, messages = load_data(upload, path)

    assert len(df) == 1
    assert df["Complaint ID"].iloc[0] == 2
    assert any("invalid 'Date received'" in message for message in messages)
