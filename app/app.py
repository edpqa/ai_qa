from flask import Flask, jsonify, request, render_template

import sys
from pathlib import Path

app = Flask(__name__)

# In-memory storage (resets when server restarts)
ITEMS = []
NEXT_ID = 1


def _ensure_repo_root_on_sys_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


def _changed_files_from_text(text: str) -> list[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


@app.get("/")
def home():
    return (
        "Hello, this is a simple QA app. "
        "Visit /dashboard for the regression testing plan."
    )


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/regression-impact", methods=["GET", "POST"])
def regression_impact():
    _ensure_repo_root_on_sys_path()
    from tools.regression_impact import analyze_change_set

    changed_files_text = ""
    result = None

    if request.method == "POST":
        changed_files_text = request.form.get("changed_files", "")
        changed_files = _changed_files_from_text(changed_files_text)
        result = analyze_change_set(
            rules_path="regression/component_map.json",
            changed_files=changed_files,
        )

    return render_template(
        "regression_impact.html",
        changed_files_text=changed_files_text,
        result=result,
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/items")
def list_items():
    return jsonify(items=ITEMS)


@app.post("/items")
def create_item():
    global NEXT_ID
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify(error="name is required"), 400

    item = {"id": NEXT_ID, "name": name.strip()}
    NEXT_ID += 1
    ITEMS.append(item)
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)
