"""CampusBot response engine with a real Gemini AI mode and a safe offline fallback.

Set GEMINI_API_KEY in the environment to enable live generative responses.
No API key is stored in source code.
"""
import json
import os
import re
import urllib.error
import urllib.request

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
SYSTEM_INSTRUCTION = """You are CampusBot, a helpful, friendly, capable general-purpose AI chatbot built as a Python college project.
Answer the user's actual question directly and naturally, not with a fixed list of supported topics. Explain concepts step-by-step when useful, use examples, and adapt detail to the question. You can help with Python, programming, study questions, writing, maths, science, general knowledge, and everyday questions.
Be honest about uncertainty. Do not invent current facts, college policies, exam dates, fees, or citations. For changing or high-stakes facts, say when you cannot verify them and suggest a reliable source. Never claim to have accessed live websites unless a tool actually did so. Do not request passwords, API keys, payment details, or unnecessary personal information.
Keep answers readable and proportionate. If the user asks for code, provide runnable code and explain how to run it. Remember the recent conversation context supplied to you."""
OFFLINE_RESPONSES = {
    "greeting": "Hi! I'm CampusBot. I can answer general questions when live AI is configured. For full conversational answers, set a Gemini API key as described in README.md. Meanwhile, try asking about Python, study topics, or type help.",
    "help": "CampusBot supports live, context-aware answers through Gemini when GEMINI_API_KEY is configured. Without a key, it uses a small offline fallback. Commands: help, clear, history, exit.",
    "thanks": "You're welcome! What else would you like to know?",
    "about": "I'm CampusBot, a Python chatbot project. With Gemini configured, I can generate conversational answers and use recent turns as context. Without it, I work in limited offline mode.",
}
FALLBACK = ("Live AI is not configured, so I can't answer that question intelligently yet. "
            "Set GEMINI_API_KEY using the setup steps in README.md, then restart CampusBot. "
            "Your API key should be kept private.")


def tokenize(text: str) -> list[str]:
    """Normalize text and split it into lowercase word tokens."""
    return re.findall(r"[a-z0-9]+", text.casefold())


def preprocess(text: str) -> list[str]:
    """Lightweight preprocessing retained for the NLP lab demonstration."""
    stop_words = {"a", "an", "the", "is", "are", "to", "for", "of", "in", "on", "and", "or", "i", "you", "me", "my", "what", "when", "where", "how", "do", "does", "can", "please"}
    return [word for word in tokenize(text) if word not in stop_words]


def classify_intent(text: str) -> str | None:
    """Identify a few common commands/intents; this is not the live AI engine."""
    words = set(tokenize(text))
    if words & {"hello", "hi", "hey", "greetings"}:
        return "greeting"
    if words & {"help", "commands", "options"}:
        return "help"
    if words & {"thanks", "thank", "thx"}:
        return "thanks"
    if "campusbot" in words and words & {"who", "what", "are", "you"}:
        return "about"
    return None


def generate_response(text: str, history: list[dict] | None = None, timeout: int = 30) -> str:
    """Generate a context-aware response with Gemini; use honest fallback without a key."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        intent = classify_intent(text)
        return OFFLINE_RESPONSES.get(intent, FALLBACK)

    turns = []
    for item in (history or [])[-12:]:
        role = item.get("role")
        content = item.get("content", "")
        if role in {"user", "model"} and isinstance(content, str) and content.strip():
            turns.append({"role": role, "parts": [{"text": content[:12000]}]})
    turns.append({"role": "user", "parts": [{"text": text[:12000]}]})
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": turns,
        "generationConfig": {"temperature": 0.65, "topP": 0.9, "maxOutputTokens": 2048},
    }
    url = API_URL.format(model=MODEL) + "?key=" + api_key
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        candidates = data.get("candidates", [])
        if not candidates:
            return "The AI provider returned no answer. Please try rephrasing your question."
        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "\n".join(part.get("text", "") for part in parts if part.get("text"))
        return answer.strip() or "I couldn't form a response for that message. Could you rephrase it?"
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
            error_obj = json.loads(body)
            detail = error_obj.get("error", {}).get("message", "")
        except Exception:
            pass
        if exc.code in (400, 401, 403):
            return "The Gemini API rejected the request or API key. Check that GEMINI_API_KEY is valid and the Generative Language API is enabled."
        if exc.code == 429:
            return "The AI service rate limit or quota was reached. Please wait and try again, or check your Gemini API quota."
        return f"The AI service returned HTTP {exc.code}. Please try again later." + (f" Details: {detail[:240]}" if detail else "")
    except (urllib.error.URLError, TimeoutError, OSError):
        return "I couldn't reach the AI service. Check your internet connection and try again."
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return "The AI service returned an unexpected response. Please try again."


def most_common_words(text: str, limit: int = 5) -> list[tuple[str, int]]:
    from collections import Counter
    return Counter(preprocess(text)).most_common(limit)
