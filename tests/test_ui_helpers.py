from src.ui import format_scorecard_html, state_to_plotly_location


def test_format_scorecard_html_escapes_dynamic_content():
    html = format_scorecard_html(
        {
            "Company": "<script>alert(1)</script>",
            "overall_risk": 72.4,
            "risk_label": "Elevated <risk>",
            "top_drivers": ["Billing <issue>"],
            "trend_direction": "Rising",
        }
    )

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "Billing &lt;issue&gt;" in html


def test_state_to_plotly_location_returns_us_state_code():
    assert state_to_plotly_location("California") == "CA"
    assert state_to_plotly_location("CA") == "CA"
    assert state_to_plotly_location("Unknown") is None
