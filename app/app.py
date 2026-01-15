from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage (resets when server restarts)
ITEMS = []
NEXT_ID = 1


@app.get("/")
def home():
    return "Hello, this is a simple QA app."


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