import os
import json
import urllib.request
import urllib.error
from flask import Flask, request, jsonify

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"

app = Flask(__name__)


def ask_groq(api_key, question):
    body = json.dumps({
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system",
             "content": "You are ThEoNe, a helpful South African AI assistant. Keep answers simple and clear."},
            {"role": "user", "content": question},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        GROQ_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "answer": data["choices"][0]["message"]["content"]}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": "HTTP " + str(e.code) + ": " + e.read().decode("utf-8")[:300]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.route("/")
def home():
    return "ThEoNe backend is alive."


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"ok": False, "error": "No question sent"}), 400

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return jsonify({"ok": False, "error": "Server has no GROQ_API_KEY set"}), 500

    result = ask_groq(api_key, question)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
