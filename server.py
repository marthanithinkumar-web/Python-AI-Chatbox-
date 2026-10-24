"""CampusBot AI backend using Groq. Keep GROQ_API_KEY in Render environment variables only."""
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
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
API_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM_INSTRUCTION = """You are CampusBot, a careful, friendly AI assistant for a college student.
Understand typos, misspellings, missing words, imperfect grammar, and follow-up questions.
Answer the actual question directly and concisely by default; explain more when needed.
Use examples when helpful. Ask for clarification only when ambiguity changes the answer.
Never invent facts, citations, dates, fees, college policies, or live status. You do not have live web search;
for changing facts, say verification may be needed and point to authoritative sources. You are not an official college service."""
requests_by_ip: dict[str, deque[float]] = defaultdict(deque)
WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 12
PROVIDER_TIMEOUT_SECONDS = 20


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
    return jsonify({"service": "CampusBot AI backend", "status": "ok", "provider": "groq", "endpoint": "/chat"})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "ai_configured": bool(os.getenv("GROQ_API_KEY", "").strip())})


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)
    if not allowed(request.remote_addr or "unknown"):
        return jsonify({"error": "Too many requests. Wait a minute and try again."}), 429
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return jsonify({"error": "CampusBot's Groq AI service is not configured yet. The owner must add GROQ_API_KEY in Render."}), 503
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Send a JSON object containing a message."}), 400
    message = data.get("message")
    history = data.get("history", [])
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(message) > 12000:
        return jsonify({"error": "Message is too long (maximum 12,000 characters)."}), 413
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    if isinstance(history, list):
        for item in history[-6:]:
            if not isinstance(item, dict):
                continue
            role, content = item.get("role"), item.get("content")
            if role == "model":
                role = "assistant"
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                messages.append({"role": role, "content": content[:1600]})
    messages.append({"role": "user", "content": message})
    payload = {"model": MODEL, "messages": messages, "temperature": 0.35, "max_tokens": 1024}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=PROVIDER_TIMEOUT_SECONDS) as response:
            result = json.loads(response.read().decode("utf-8"))
        answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        if isinstance(answer, list):
            answer = "\\n".join(part.get("text", "") for part in answer if isinstance(part, dict))
        answer = answer.strip() if isinstance(answer, str) else ""
        if not answer:
            return jsonify({"error": "The AI provider returned no readable answer. Please rephrase."}), 502
        return jsonify({"reply": answer})
    except urllib.error.HTTPError as exc:
        # Log provider diagnostics only; never log request headers or API keys.
        try:
            raw_body = exc.read().decode("utf-8", errors="replace")[:1200]
        except Exception:
            raw_body = ""
        detail = ""
        error_code = ""
        try:
            details = json.loads(raw_body)
            err = details.get("error", {})
            if isinstance(err, dict):
                detail = str(err.get("message", "") or "")
                error_code = str(err.get("code", "") or err.get("type", "") or "")
            elif err:
                detail = str(err)
            if not detail:
                detail = str(details.get("message", "") or "")
        except (ValueError, AttributeError, TypeError):
            pass
        app.logger.warning(
            "Groq request failed: model=%s http=%s error_code=%s message=%s body=%s",
            MODEL, exc.code, error_code[:120], detail[:300], raw_body[:500]
        )
        if exc.code == 429:
            return jsonify({"error": "The AI provider rate limit was reached. Please wait a moment and try again."}), 429
        if exc.code == 401:
            return jsonify({"error": "Groq authentication failed. Verify that Render's GROQ_API_KEY is active and belongs to the intended Groq project."}), 502
        if exc.code == 403:
            return jsonify({"error": "Groq denied this request (HTTP 403). Check the API key's organization/project and organization/project permissions. The owner can see the specific provider error in Render logs."}), 502
        if exc.code == 404:
            return jsonify({"error": "The configured AI model is unavailable. The owner must check GROQ_MODEL in Render."}), 502
        return jsonify({"error": "The AI provider is temporarily unavailable. Please try again."}), 502
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        app.logger.warning("Groq provider connection failed or timed out")
        return jsonify({"error": "The AI provider could not be reached. Please try again."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
