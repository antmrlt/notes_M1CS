import requests
from flask import Flask, jsonify

app = Flask(__name__)

NOTES_URL = "https://raw.githubusercontent.com/Gladrat/notes_M1CS/main/notes.json"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
