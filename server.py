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
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
SYSTEM_INSTRUCTION = """You are CampusBot, a careful, friendly AI assistant for a college student.
Understand typos, misspellings, missing words, imperfect grammar, and follow-up questions.
Answer the actual question directly and concisely by default; explain more when needed.
Use examples when helpful. Ask for clarification only when ambiguity changes the answer.
Never invent facts, citations, dates, fees, college policies, or live status. You do not have live web search;
for changing facts, say verification may be needed and point to authoritative sources. You are not an official college service."""
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
    # Send only the six most recent turns and cap each history message to limit network/prompt work.
    if isinstance(history, list):
        for item in history[-6:]:
            if not isinstance(item, dict):
                continue
            role, content = item.get("role"), item.get("content")
            if role in ("user", "model") and isinstance(content, str) and content.strip():
                turns.append({"role": role, "parts": [{"text": content[:1600]}]})
    turns.append({"role": "user", "parts": [{"text": message}]})
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": turns,
        # Keep the quality-preserving 1,024-token ceiling; short answers finish sooner naturally.
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
        # Log only sanitized provider diagnostics (never the API key or request payload).
        try:
            provider_data = json.loads(exc.read().decode("utf-8", errors="replace"))
            provider_error = provider_data.get("error", {})
            provider_status = provider_error.get("status", "") if isinstance(provider_error, dict) else ""
            provider_message = provider_error.get("message", "") if isinstance(provider_error, dict) else ""
        except (ValueError, AttributeError):
            provider_status, provider_message = "", ""
        app.logger.warning(
            "Gemini request failed: model=%s http=%s status=%s message=%s",
            MODEL, exc.code, provider_status, provider_message[:300],
        )
        if exc.code == 429:
            return jsonify({"error": "Shared AI quota/rate limit reached. Please wait a minute and try again."}), 429
        if exc.code in (401, 403):
            return jsonify({"error": "Gemini rejected the backend API key or this project's model access. The CampusBot owner must check the Gemini API key and access settings."}), 502
        if exc.code == 404:
            return jsonify({"error": "The configured Gemini model is unavailable to this API project. The backend has been updated to use the current default model; if this persists, the owner must check GEMINI_MODEL and Gemini model access."}), 502
        if exc.code == 400:
            return jsonify({"error": "Gemini rejected the request format or model settings. Check the backend logs for sanitized diagnostic details."}), 502
        return jsonify({"error": "The AI provider is temporarily unavailable. Please try again."}), 502
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return jsonify({"error": "The AI provider could not be reached. Please try again."}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
