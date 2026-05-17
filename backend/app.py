import base64
import json
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

NOTES_API_URL = "https://api.github.com/repos/Gladrat/notes_M1CS/contents/notes.json"
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

def fetch_notes():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "notes-app"}
    token = os.environ.get("NOTES_API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(NOTES_API_URL, timeout=5, headers=headers)
    r.raise_for_status()
    content = base64.b64decode(r.json()["content"]).decode("utf-8")
    data = json.loads(content)
    if "etudiants" not in data:
        raise ValueError("invalid structure")
    return data


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "assets"), filename)


@app.route("/notes")
def notes():
    try:
        data = fetch_notes()
    except Exception:
        return jsonify({"error": "Service temporairement indisponible"}), 503

    student_id = request.args.get("id")
    if student_id is not None:
        try:
            idx = int(student_id)
            etudiants = [data["etudiants"][idx]]
        except (ValueError, IndexError):
            return jsonify({"error": "Not found"}), 404
        return jsonify({**data, "etudiants": etudiants})

    return jsonify(data)


@app.route("/search")
def search():
    try:
        data = fetch_notes()
    except Exception:
        return jsonify({"error": "Service temporairement indisponible"}), 503

    q = request.args.get("q", "").lower()
    results = [
        e for e in data["etudiants"]
        if q in e["nom"].lower() or q in e["prenom"].lower()
    ]
    return jsonify({**data, "etudiants": results})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
