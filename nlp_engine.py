"""CampusBot response engine with Gemini AI and transparent offline behavior.

Set GEMINI_API_KEY in the environment to enable generative answers.
Never store API keys in this repository.
"""
import json
import os
import re
import urllib.error
import urllib.request

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_INSTRUCTION = """You are CampusBot, a careful, capable, friendly AI assistant for a college student. Your goal is to understand the meaning of the question and answer it correctly, not merely match keywords.

UNDERSTAND FIRST
- Identify what the user is actually asking, including constraints, context, and the desired output.
- Use earlier messages when a follow-up depends on them. Do not make the user repeat context already provided.
- If the request has more than one reasonable interpretation and the difference changes the answer, ask one concise clarification question. Otherwise state a reasonable assumption and answer.
- For multi-part questions, address every part. Do not ignore details or answer a nearby but different question.

ANSWER QUALITY
- Start with the direct answer, then explain why and how. Use clear, natural language appropriate for a student.
- For learning questions, explain unfamiliar terms, give a small concrete example, and show steps when that helps understanding.
- For programming requests, provide runnable code when appropriate, explain where it belongs, how to run it, expected output, and important edge cases. Check the logic for consistency before responding.
- For calculations, show the formula and enough working to let the user verify the result.
- For comparisons, state the criteria and explain the meaningful differences.
- Use headings or bullets only when they improve readability. Avoid generic filler, repeated disclaimers, and overly short answers to complex questions.
- Be concise for simple questions and thorough for difficult ones. If the user asks for a particular format or level, follow it.
- Think carefully through the problem before answering, but do not reveal private hidden chain-of-thought. Give a concise explanation or verification summary instead.

ACCURACY AND HONESTY
- Distinguish established facts from assumptions and uncertainty. Never invent numbers, quotes, citations, results, sources, college policies, exam dates, fees, or live status.
- For time-sensitive facts, say if you cannot verify them live and point to an authoritative source.
- If a question depends on a file, codebase, or source that you have not received, ask for it instead of pretending to inspect it.
- If you do not know, say so and suggest a practical way to check.
- Never claim to have used a tool, browsed a site, executed code, or verified a result unless that actually happened.

SAFETY AND PRIVACY
- Do not ask for passwords, API keys, payment credentials, or unnecessary sensitive data.
- For medical, legal, financial, or safety-critical matters, give careful general information and recommend a qualified or official source where appropriate.
- You are not an official college service. Direct users to official college channels for authoritative, changing information.

You can help with programming, mathematics, science, writing, study topics, general knowledge, planning, and everyday questions. Answer the actual question rather than forcing it into a fixed list of topics."""

OFFLINE_RESPONSES = {
    "greeting": "Hi! I'm CampusBot. Live AI is needed for flexible, detailed answers. Configure GEMINI_API_KEY as explained in README.md, then restart the app.",
    "help": "Ask a question in your own words. With Gemini configured, CampusBot can explain topics and handle follow-ups. Commands: help, clear, history, exit.",
    "thanks": "You're welcome! What would you like to explore next?",
    "about": "I'm CampusBot, a Python chatbot project. Live mode uses Gemini to generate flexible answers and follow-ups; without an API key, I can only provide limited built-in replies.",
}
FALLBACK = (
    "Live AI is not configured, so I can't reliably analyze and answer open-ended questions yet. "
    "Set GEMINI_API_KEY using the safe setup steps in README.md, then restart CampusBot. "
    "Do not put your key in source code or commit it to GitHub."
)


def tokenize(text: str) -> list[str]:
    """Normalize text and split it into lowercase word tokens."""
    return re.findall(r"[a-z0-9]+", text.casefold())


def preprocess(text: str) -> list[str]:
    """Lightweight NLP preprocessing retained for the Python lab demonstration."""
    stop_words = {
        "a", "an", "the", "is", "are", "to", "for", "of", "in", "on",
        "and", "or", "i", "you", "me", "my", "what", "when", "where",
        "how", "do", "does", "can", "please",
    }
    return [word for word in tokenize(text) if word not in stop_words]


def classify_intent(text: str) -> str | None:
    """Identify basic commands/intents; not the live generative AI engine."""
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


def generate_response(text: str, history: list[dict] | None = None, timeout: int = 45) -> str:
    """Generate an answer using Gemini and recent conversation context."""
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
        "generationConfig": {
            "temperature": 0.35,
            "topP": 0.9,
            "maxOutputTokens": 4096,
        },
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
            feedback = data.get("promptFeedback", {}).get("blockReason")
            if feedback:
                return f"The AI provider blocked this request ({feedback}). Please rephrase the question."
            return "The AI provider returned no answer. Please try rephrasing your question."
        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        answer = "\n".join(part.get("text", "") for part in parts if part.get("text"))
        if not answer.strip():
            reason = candidate.get("finishReason", "")
            if reason:
                return f"The AI response ended without readable text (reason: {reason}). Please try again."
            return "I couldn't form a useful response. Could you rephrase the question?"
        return answer.strip()
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
            error_obj = json.loads(body)
            detail = error_obj.get("error", {}).get("message", "")
        except Exception:
            detail = ""
        if exc.code in (400, 401, 403):
            return "Gemini rejected the request or API key. Check that GEMINI_API_KEY is valid, the selected model is available, and the Generative Language API is enabled."
        if exc.code == 404:
            return f"The configured Gemini model '{MODEL}' was not found or is unavailable to this key. Check GEMINI_MODEL in README.md."
        if exc.code == 429:
            return "Gemini's rate limit or quota was reached. Wait and try again, or check your Google AI Studio quota."
        message = f"The AI service returned HTTP {exc.code}. Please try again later."
        return message + (f" Provider detail: {detail[:300]}" if detail else "")
    except (urllib.error.URLError, TimeoutError, OSError):
        return "I couldn't reach Gemini. Check the internet connection and try again."
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return "Gemini returned an unexpected response. Please try again."


def most_common_words(text: str, limit: int = 5) -> list[tuple[str, int]]:
    from collections import Counter
    return Counter(preprocess(text)).most_common(limit)
