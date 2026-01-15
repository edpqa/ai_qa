from tools.regression_impact import analyze_change_set


def test_ui_change_recommends_medium():
    result = analyze_change_set(
        rules_path="regression/component_map.json",
        changed_files=["app/templates/dashboard.html"],
    )
    assert result["recommended_regression_level"] == "medium"


def test_api_change_recommends_high():
    result = analyze_change_set(
        rules_path="regression/component_map.json",
        changed_files=["app/app.py"],
    )
    assert result["recommended_regression_level"] == "high"


def test_test_only_change_recommends_default_low():
    result = analyze_change_set(
        rules_path="regression/component_map.json",
        changed_files=["tests/test_app.py"],
    )
    assert result["recommended_regression_level"] == "low"


def test_ui_plus_api_recommends_high():
    result = analyze_change_set(
        rules_path="regression/component_map.json",
        changed_files=["app/app.py", "app/templates/dashboard.html"],
    )
    assert result["recommended_regression_level"] == "high"

