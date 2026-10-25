"""CampusBot — standalone Tkinter desktop AI chatbot.

Requirements: Python 3.10+, Tkinter, and internet for shared live AI.
The shared backend is the default; friends do not need a Gemini API key.
No third-party Python packages are required for the desktop client.
"""
from __future__ import annotations

import csv
import json
import os
import queue
import re
import unicodedata
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

APP_NAME = "CampusBot"
BACKEND_URL = os.getenv(
    "CAMPUSBOT_BACKEND_URL",
    "https://campusbot-ai-backend.onrender.com",
).strip()
HISTORY_FILE = Path(__file__).with_name("chat_history.csv")
HISTORY_FIELDS = ["timestamp", "user", "bot", "nlp_tokens", "nlp_keywords", "nlp_intent", "nlp_question_type", "nlp_sentiment"]



# Lightweight, dependency-free NLP for local message analysis.
# It never rewrites the message sent to the AI backend or changes the GUI.
NLP_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "to", "of", "in", "on",
    "at", "for", "from", "by", "with", "is", "am", "are", "was", "were",
    "be", "been", "do", "does", "did", "can", "could", "would", "should",
    "will", "i", "me", "my", "we", "our", "you", "your", "he", "she",
    "it", "they", "them", "this", "that", "these", "those", "what", "when",
    "where", "why", "how", "who", "which", "please", "just", "also", "have",
    "has", "had",
}
POSITIVE_WORDS = {
    "good", "great", "happy", "love", "helpful", "thanks", "excellent",
    "perfect", "clear", "success", "correct", "working",
}
NEGATIVE_WORDS = {
    "bad", "poor", "hate", "broken", "error", "failed", "problem", "issue",
    "wrong", "terrible", "confusing", "difficult", "slow", "crash", "bug",
}
NEGATION_WORDS = {"not", "no", "never", "cannot", "can't", "don't", "doesn't", "isn't"}
INTENSIFIERS = {"very", "really", "extremely", "too", "absolutely"}
INTENT_PHRASES = {
    "greeting": {"good morning", "good afternoon", "good evening", "how are you"},
    "farewell": {"see you", "good night", "talk later", "exit chat"},
    "thanks": {"thank you", "thanks a lot", "much appreciated", "that helped"},
    "troubleshooting": {"not working", "does not work", "how to fix", "error message", "failed to run"},
    "summarization": {"summarize this", "summary of", "in short", "key points"},
    "translation": {"translate to", "translate into", "in english", "in hindi", "meaning of"},
    "recommendation": {"recommend me", "suggest some", "which is best", "best option"},
    "python_topic": {"what is python", "python programming", "why use python"},
    "variables": {"what is a variable", "python variables", "create a variable"},
    "loops": {"what is a loop", "for loop", "while loop", "difference between for and while"},
    "functions": {"what is a function", "define a function", "python def example"},
    "lists": {"what is a list", "python list example", "add an item to a list"},
    "nlp_topic": {"what is nlp", "natural language processing", "nlp full form"},
    "tokenization": {"what is tokenization", "tokens in nlp", "split text into words"},
    "tfidf": {"what is tf-idf", "explain tfidf", "inverse document frequency"},
    "classification": {"text classification", "logistic regression", "intent classification"},
    "similarity": {"cosine similarity", "text similarity"},
    "project": {"explain this project", "how does campusbot work", "project architecture"},
    "study_tips": {"study tips", "prepare for exams", "study better"},
    "help": {"what topics do you know", "what can i ask", "show example questions"},
    "explanation": {"what is", "what are", "how does", "how do", "explain to me", "difference between"},
}
# Broad fallback categories only; specific topics are matched by INTENT_PHRASES.
INTENT_KEYWORDS = {
    "greeting": {"hello", "hi", "hey"},
    "farewell": {"bye", "goodbye", "exit"},
    "thanks": {"thanks", "thank", "appreciate"},
    "coding_help": {"python", "code", "coding", "program", "bug", "error", "api", "sql", "java"},
    "study_help": {"study", "exam", "college", "assignment", "project", "learn", "lab", "notes"},
    "troubleshooting": {"fix", "broken", "failed", "issue", "problem", "crash", "wrong"},
    "summarization": {"summarize", "summary", "shorten", "brief"},
    "translation": {"translate", "translation", "language", "meaning"},
    "recommendation": {"recommend", "suggest", "choose", "compare", "best"},
    "explanation": {"explain", "define", "definition", "difference", "describe"},
}
QUESTION_STARTERS = {"who", "what", "when", "where", "why", "how", "which"}


def analyze_text(text: str) -> dict[str, str]:
    """Extract meaningful tokens, key phrases, intent, question type, and sentiment."""
    normalized = unicodedata.normalize("NFKC", text).casefold().strip()
    tokens = re.findall(r"[^\W_]+(?:['’][^\W_]+)?", normalized, flags=re.UNICODE)
    tokens = [token.replace("’", "'") for token in tokens]
    meaningful = [
        token for token in tokens
        if token not in NLP_STOP_WORDS and token not in {"don't", "doesn't", "isn't", "can't", "won't"}
        and len(token) > 1
    ]

    frequency: dict[str, int] = {}
    for token in meaningful:
        frequency[token] = frequency.get(token, 0) + 1
    phrase_candidates = [
        f"{left} {right}" for left, right in zip(tokens, tokens[1:])
        if left not in NLP_STOP_WORDS and right not in NLP_STOP_WORDS
        and len(left) > 1 and len(right) > 1
    ]
    unique_phrases = list(dict.fromkeys(phrase_candidates))
    ranked_phrases = sorted(
        unique_phrases,
        key=lambda phrase: (-phrase_candidates.count(phrase), normalized.find(phrase)),
    )
    ranked_tokens = sorted(frequency, key=lambda token: (-frequency[token], normalized.find(token)))
    keywords = list(dict.fromkeys(ranked_phrases + ranked_tokens))[:8]

    phrase_intents = [
        intent for intent, phrases in INTENT_PHRASES.items()
        if any(phrase in normalized for phrase in phrases)
    ]
    scores = {
        intent: sum(token in words for token in tokens)
        for intent, words in INTENT_KEYWORDS.items()
    }
    if "troubleshooting" in phrase_intents:
        intent = "troubleshooting"
    elif phrase_intents:
        intent = phrase_intents[0]
    else:
        intent = max(scores, key=scores.get)
        if scores[intent] == 0:
            intent = "question" if "?" in text or (tokens and tokens[0] in QUESTION_STARTERS) else "general"

    positive = negative = 0
    for index, token in enumerate(tokens):
        if token in POSITIVE_WORDS or token in NEGATIVE_WORDS:
            previous = tokens[max(0, index - 3):index]
            negated = any(word in NEGATION_WORDS for word in previous)
            intensified = any(word in INTENSIFIERS for word in tokens[max(0, index - 2):index])
            weight = 2 if intensified else 1
            is_positive = token in POSITIVE_WORDS
            if negated:
                is_positive = not is_positive
            if is_positive:
                positive += weight
            else:
                negative += weight
    sentiment = "positive" if positive > negative else "negative" if negative > positive else "neutral"

    first = tokens[0] if tokens else ""
    question_types = {
        "what": "definition/information", "who": "person", "when": "time/date",
        "where": "location", "why": "reason", "how": "method/process",
        "which": "choice/comparison", "whose": "ownership", "whom": "person",
    }
    question_type = question_types.get(first, "yes/no or general question" if "?" in text else "statement/request")
    return {
        "nlp_tokens": " ".join(meaningful[:30]),
        "nlp_keywords": ", ".join(keywords),
        "nlp_intent": intent,
        "nlp_question_type": question_type,
        "nlp_sentiment": sentiment,
    }


def generate_response(
    text: str,
    history: list[dict[str, str]] | None = None,
    timeout: int = 60,
) -> str:
    """Send a chat turn to the shared CampusBot AI backend."""
    if not BACKEND_URL:
        return (
            "CampusBot's shared AI service URL is not configured. "
            "Restore the default CAMPUSBOT_BACKEND_URL setting."
        )

    payload = {"message": text[:12000], "history": (history or [])[-8:]}
    request = urllib.request.Request(
        BACKEND_URL.rstrip("/") + "/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data.get("reply", "")
        if isinstance(answer, str) and answer.strip():
            return answer.strip()
        return "CampusBot's AI service returned an empty answer. Please try again."
    except urllib.error.HTTPError as exc:
        try:
            data = json.loads(exc.read().decode("utf-8", errors="replace"))
            detail = data.get("error", "")
        except (ValueError, AttributeError):
            detail = ""
        return detail or f"CampusBot AI service returned HTTP {exc.code}. Please try again."
    except (urllib.error.URLError, TimeoutError, OSError):
        return (
            "Couldn't reach CampusBot's shared AI service. Check your internet "
            "connection or try again later."
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return "CampusBot's shared AI service returned an unexpected response. Please try again."


def append_chat(user_message: str, bot_message: str) -> None:
    """Save a chat exchange and local NLP features, preserving older CSV rows."""
    nlp = analyze_text(user_message)
    exists = HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0
    if exists:
        with HISTORY_FILE.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            old_fields = reader.fieldnames or []
            old_rows = list(reader)
        if old_fields != HISTORY_FIELDS:
            with HISTORY_FILE.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
                writer.writeheader()
                for old_row in old_rows:
                    writer.writerow({field: old_row.get(field, "") for field in HISTORY_FIELDS})
    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user": user_message,
            "bot": bot_message,
            **nlp,
        })

def read_history() -> list[dict[str, str]]:
    """Read locally saved exchanges."""
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def add_turn(
    history: list[dict[str, str]], user: str, bot: str
) -> list[dict[str, str]]:
    """Return bounded conversation context for the next AI request."""
    return [
        *history,
        {"role": "user", "content": user},
        {"role": "model", "content": bot},
    ][-12:]


def run_gui() -> None:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext

    class CampusBotGUI:
        def __init__(self, root: tk.Tk):
            self.root = root
            root.title("CampusBot - AI Chatbot")
            root.geometry("850x680")
            root.minsize(560, 460)
            root.configure(bg="#f3f5f9")

            self.history: list[dict[str, str]] = []
            self.results: queue.Queue = queue.Queue()
            self.busy = False

            header = tk.Frame(root, bg="#18243a", padx=22, pady=16)
            header.pack(fill="x")
            tk.Label(
                header, text="CampusBot", font=("Segoe UI", 20, "bold"),
                fg="white", bg="#18243a",
            ).pack(anchor="w")
            self.status = tk.Label(
                header, text="Shared AI service • Ready",
                font=("Segoe UI", 10), fg="#cbd5e1", bg="#18243a",
            )
            self.status.pack(anchor="w", pady=(3, 0))

            body = tk.Frame(root, bg="#f3f5f9", padx=18, pady=14)
            body.pack(fill="both", expand=True)
            self.chat = scrolledtext.ScrolledText(
                body, wrap="word", state="disabled",
                font=("Segoe UI", 11), padx=14, pady=12,
                bg="white", fg="#172033", relief="flat", borderwidth=0,
            )
            self.chat.pack(fill="both", expand=True)
            self.chat.tag_config("system", foreground="#64748b", spacing1=5, spacing3=8)
            self.chat.tag_config("you", foreground="#2459a9",
                                 font=("Segoe UI", 10, "bold"), spacing1=8)
            self.chat.tag_config("bot", foreground="#172033",
                                 font=("Segoe UI", 10, "bold"), spacing1=8)
            self.chat.tag_config("answer", foreground="#172033",
                                 lmargin1=8, lmargin2=8, spacing3=8)
            self.write(
                "CampusBot",
                "Hi! Ask a question below. Follow-ups use this conversation. "
                "Answered messages are saved locally.",
                "system",
            )

            compose = tk.Frame(root, bg="#f3f5f9", padx=18)
            compose.pack(fill="x", pady=(0, 14))
            self.entry = tk.Entry(
                compose, font=("Segoe UI", 11), relief="solid", bd=1
            )
            self.entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
            self.entry.bind("<Return>", self.send_event)
            self.send_button = tk.Button(
                compose, text="Send", command=self.send, bg="#2459a9",
                fg="white", relief="flat", padx=18, pady=9, cursor="hand2",
            )
            self.send_button.pack(side="left")

            controls = tk.Frame(root, bg="#f3f5f9", padx=18)
            controls.pack(fill="x", pady=(0, 14))
            tk.Button(
                controls, text="Clear conversation", command=self.clear,
                relief="flat", cursor="hand2",
            ).pack(side="left")
            tk.Button(
                controls, text="Show saved history", command=self.show_history,
                relief="flat", cursor="hand2",
            ).pack(side="left", padx=(8, 0))
            tk.Label(
                controls, text="Don't enter passwords or API keys.",
                bg="#f3f5f9", fg="#64748b", font=("Segoe UI", 9),
            ).pack(side="right")

            self.entry.focus_set()
            root.protocol("WM_DELETE_WINDOW", self.close)
            root.after(100, self.poll)

        def write(self, speaker: str, message: str, tag: str) -> None:
            self.chat.configure(state="normal")
            self.chat.insert(
                "end", speaker + "\n",
                tag if tag in {"system", "you", "bot"} else "system",
            )
            self.chat.insert("end", message + "\n\n", "answer")
            self.chat.configure(state="disabled")
            self.chat.see("end")

        def send_event(self, _event=None):
            self.send()
            return "break"

        def send(self) -> None:
            message = self.entry.get().strip()
            if not message or self.busy:
                return

            self.entry.delete(0, "end")
            self.write("You", message, "you")
            self.busy = True
            self.send_button.configure(state="disabled")
            self.status.configure(text="Thinking…")
            threading.Thread(
                target=self.generate_in_background,
                args=(message, list(self.history)),
                daemon=True,
            ).start()

        def generate_in_background(
            self, message: str, previous: list[dict[str, str]]
        ) -> None:
            try:
                reply = generate_response(message, previous)
                # A local history write failure must not discard a valid AI reply.
                try:
                    append_chat(message, reply)
                except OSError:
                    pass
                self.results.put(("ok", reply, add_turn(previous, message, reply)))
            except Exception as exc:
                self.results.put(
                    ("error", f"Unexpected application error: {exc}", previous)
                )

        def poll(self) -> None:
            try:
                while True:
                    kind, reply, updated = self.results.get_nowait()
                    if kind == "ok":
                        self.history = updated
                        self.write("CampusBot", reply, "bot")
                    else:
                        self.write("CampusBot", reply, "system")
                    self.busy = False
                    self.send_button.configure(state="normal")
                    self.status.configure(text="Shared AI service • Ready")
                    self.entry.focus_set()
            except queue.Empty:
                pass
            self.root.after(100, self.poll)

        def clear(self) -> None:
            if self.busy:
                self.write(
                    "CampusBot",
                    "Please wait for the current answer before clearing context.",
                    "system",
                )
                return
            self.history.clear()
            self.chat.configure(state="normal")
            self.chat.delete("1.0", "end")
            self.chat.configure(state="disabled")
            self.write(
                "CampusBot",
                "Conversation context cleared. Saved CSV history remains available.",
                "system",
            )
            self.status.configure(text="Conversation cleared")

        def show_history(self) -> None:
            rows = read_history()
            if not rows:
                self.write("CampusBot", "No saved chat history yet.", "system")
                return
            self.write(
                "CampusBot",
                f"Showing the latest {min(10, len(rows))} saved turns:",
                "system",
            )
            for row in rows[-10:]:
                self.write("You", row.get("user", ""), "you")
                self.write("CampusBot", row.get("bot", ""), "bot")

        def close(self) -> None:
            if self.busy and not messagebox.askyesno(
                "CampusBot", "An answer is still being generated. Close anyway?"
            ):
                return
            self.root.destroy()

    root = tk.Tk()
    CampusBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        run_gui()
    except ImportError as exc:
        raise SystemExit(
            f"Tkinter is unavailable. Repair Python with Tcl/Tk enabled. Details: {exc}"
        )
