import os

from src.assistant import answer_question
from src.data_loader import load_sample_data
from src.transform import transform_complaint_data


def _sample_df():
    path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "cfpb_complaints_sample.csv")
    return transform_complaint_data(load_sample_data(path))


def test_answer_question_compares_two_named_companies():
    answer = answer_question(_sample_df(), "how is experian compared with equifax?")

    assert "Experian" in answer["summary"]
    assert "Equifax" in answer["summary"]
    assert "complaints" in answer["summary"]
    assert answer["chart"]["type"] == "bar"
    assert set(answer["chart"]["data"]["Company"]) == {"Experian", "Equifax"}


def test_answer_question_handles_empty_filtered_data():
    df = _sample_df().iloc[0:0]

    answer = answer_question(df, "Which companies have the highest fraud risk?")

    assert answer["chart"] is None
    assert "No complaint data" in answer["summary"]
