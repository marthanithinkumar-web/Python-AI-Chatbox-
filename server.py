"""CampusBot shared AI backend. Keep GEMINI_API_KEY in Render environment variables only."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections import defaultdict, deque

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 48 * 1024
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
SYSTEM_INSTRUCTION = """You are CampusBot, a careful, capable, friendly AI assistant for a college student.
Understand context, typos, misspellings, missing words, imperfect grammar, and follow-up questions.
Answer every meaningful part of the user's question. Start with the direct answer and be concise by default;
expand when the question needs explanation. Give examples when helpful. Ask a short clarification only when
ambiguity materially changes the answer. Never invent facts, citations, dates, fees, college policies, or live status.
You do not have live web search in this application. For changing facts, clearly say when verification is needed
and direct the user to authoritative current sources. You are not an official college service."""
requests_by_ip: dict[str, deque[float]] = defaultdict(deque)
WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 12


def allowed(ip: str) -> bool:
    now = time.monotonic()
    hits = requests_by_ip[ip]
    while hits and now - hits[0] > WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= MAX_REQUESTS_PER_WINDOW:
        return False
    hits.append(now)
    return True


@app.after_request
def cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/")
def index():
    return jsonify({"service": "CampusBot AI backend", "status": "ok", "endpoint": "/chat"})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "ai_configured": bool(os.getenv("GEMINI_API_KEY", "").strip())})


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)
    if not allowed(request.remote_addr or "unknown"):
        return jsonify({"error": "Too many requests. Wait a minute and try again."}), 429
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return jsonify({"error": "CampusBot's shared AI service is not configured yet. Please try again later."}), 503
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Send a JSON object containing a message."}), 400
    message = data.get("message")
    history = data.get("history", [])
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(message) > 12000:
        return jsonify({"error": "Message is too long (maximum 12,000 characters)."}), 413
    turns = []
    # Bound context by both turn count and per-message size to reduce request latency.
    if isinstance(history, list):
        for item in history[-8:]:
            if not isinstance(item, dict):
                continue
            role, content = item.get("role"), item.get("content")
            if role in ("user", "model") and isinstance(content, str) and content.strip():
                turns.append({"role": role, "parts": [{"text": content[:2500]}]})
    turns.append({"role": "user", "parts": [{"text": message}]})
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": turns,
        "generationConfig": {"temperature": 0.35, "topP": 0.9, "maxOutputTokens": 1024},
    }
    url = API_URL.format(model=MODEL) + "?key=" + api_key
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            result = json.loads(response.read().decode("utf-8"))
        candidates = result.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        answer = "\n".join(part.get("text", "") for part in parts if part.get("text")).strip()
        if not answer:
            return jsonify({"error": "The AI provider returned no readable answer. Please rephrase."}), 502
        return jsonify({"reply": answer})
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            return jsonify({"error": "Shared AI quota/rate limit reached. Please wait and try again."}), 429
        if exc.code in (400, 401, 403, 404):
            app.logger.warning("Gemini rejected request: HTTP %s", exc.code)
            return jsonify({"error": "The shared AI service needs configuration or has reached a provider limit. Please contact the CampusBot owner."}), 502
        return jsonify({"error": "The AI provider is temporarily unavailable. Please try again."}), 502
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return jsonify({"error": "The AI provider could not be reached. Please try again."}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
