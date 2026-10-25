"""CampusBot: a single-file Python desktop chatbot focused on NLP.

Core: text normalization, tokenization, TF-IDF, intent classification, and
similarity-based fallback. Optional: Groq chat completions for broader answers.
Set GROQ_API_KEY in the environment to enable the optional online AI feature.
"""
from __future__ import annotations

import csv
import json
import os
import random
import re
import threading
import queue
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

APP_NAME = "CampusBot"
BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "chat_history.csv"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
HISTORY_FIELDS = ["timestamp", "user", "bot"]

# Small, embedded training set: no separate JSON dataset is required.
TRAINING_DATA = [
    ("greeting", ["hi", "hello", "hey", "good morning", "hello there", "hii"], [
        "Hello! What would you like to learn today?",
        "Hi! Ask me a question and I will try to help."
    ]),
    ("goodbye", ["bye", "goodbye", "see you later", "exit chat"], [
        "Goodbye! Keep learning and have a great day."
    ]),
    ("thanks", ["thanks", "thank you", "that helped", "thanks a lot"], [
        "You're welcome! Feel free to ask another question."
    ]),
    ("python", ["what is python", "explain python programming", "define python", "why use python"], [
        "Python is a high-level, general-purpose programming language known for readable syntax. It is used in automation, web development, data analysis, and machine learning."
    ]),
    ("variables", ["what is a variable in python", "explain python variables", "how to create a variable", "variable example"], [
        "A variable is a name that refers to a value. For example, name = 'Sam' and marks = 95. Python infers the value's type when you assign it."
    ]),
    ("loops", ["what is a loop", "explain for loop", "explain while loop", "difference between for and while loop"], [
        "A loop repeats code. A for loop iterates over a sequence; a while loop repeats while its condition is true. Example: for i in range(3): print(i)"
    ]),
    ("functions", ["what is a function in python", "explain functions", "how to define a function", "python def example"], [
        "A function is a reusable block of code. Example: def add(a, b): return a + b. Call add(2, 3) to get 5."
    ]),
    ("lists", ["what is a list in python", "explain python list", "python list example", "how to add an item to a list"], [
        "A list is an ordered, changeable collection. Example: items = ['pen', 'book']; items.append('bag') adds an item. Indexing starts at zero."
    ]),
    ("nlp", ["what is nlp", "define natural language processing", "explain natural language processing", "nlp full form"], [
        "Natural Language Processing (NLP) is a field of AI that helps computers process human language. Tasks include tokenization, text classification, sentiment analysis, and information extraction."
    ]),
    ("tokenization", ["what is tokenization", "explain tokens in nlp", "how does tokenization work", "split text into words"], [
        "Tokenization divides text into smaller units called tokens, such as words. For example, 'I like Python' can become ['I', 'like', 'Python']."
    ]),
    ("tfidf", ["what is tf idf", "explain tfidf", "term frequency inverse document frequency", "how does tfidf work"], [
        "TF-IDF means Term Frequency–Inverse Document Frequency. It converts text into numeric features, giving weight to terms based on their frequency in one text and rarity across the collection."
    ]),
    ("classification", ["what is text classification", "explain logistic regression", "what is intent classification", "how does a chatbot identify intent"], [
        "Intent classification predicts the purpose of a message, such as greeting or asking about Python. CampusBot uses TF-IDF text features with Logistic Regression to choose an intent."
    ]),
    ("similarity", ["what is cosine similarity", "how does text similarity work", "why use similarity in a chatbot"], [
        "Cosine similarity compares the direction of text vectors. A higher score usually means the texts are more alike. CampusBot uses similarity to avoid answering when a message is unlike its training examples."
    ]),
    ("project", ["explain this project", "how does campusbot work", "project architecture", "what technologies are used"], [
        "CampusBot is a Python desktop chatbot. It normalizes and tokenizes a message, transforms it with TF-IDF, predicts a likely intent, checks similarity, and selects a matching response. If configured, Groq can generate a broader answer."
    ]),
    ("study_tips", ["give me study tips", "how to prepare for exams", "how can i study better", "help me focus on studying"], [
        "Break the syllabus into small goals, practise questions without looking at notes, review mistakes, and revisit difficult topics over several days. Short focused sessions can help."
    ]),
    ("help", ["help", "what topics do you know", "what can i ask", "show example questions"], [
        "Try asking about Python, variables, loops, functions, lists, NLP, tokenization, TF-IDF, text classification, or this project. With a Groq API key, broader questions can also be answered online."
    ]),
]

STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "on", "in", "at", "to", "of",
    "for", "and", "or", "what", "how", "why", "when", "where", "who",
    "can", "do", "does", "i", "me", "my", "you", "your", "it", "this",
    "that", "with", "about", "please", "tell", "explain", "define"
}

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as exc:
    raise SystemExit(
        "CampusBot requires scikit-learn. Install it with: python -m pip install -r requirements.txt"
    ) from exc


def normalize_text(text: str) -> str:
    """Lowercase and clean punctuation while retaining words and numbers."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    """Simple word tokenizer used during NLP preprocessing."""
    return re.findall(r"[a-z0-9']+", normalize_text(text))


class NLPChatbot:
    """Train a local TF-IDF and Logistic Regression intent model."""

    def __init__(self):
        self.patterns: list[str] = []
        self.labels: list[str] = []
        self.responses: dict[str, list[str]] = {}
        for tag, patterns, responses in TRAINING_DATA:
            self.responses[tag] = responses
            for pattern in patterns:
                cleaned = normalize_text(pattern)
                if cleaned:
                    self.patterns.append(cleaned)
                    self.labels.append(tag)
        self.vectorizer = TfidfVectorizer(
            tokenizer=tokenize, token_pattern=None, lowercase=False,
            ngram_range=(1, 2), sublinear_tf=True
        )
        self.pattern_matrix = self.vectorizer.fit_transform(self.patterns)
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        self.classifier.fit(self.pattern_matrix, self.labels)

    def predict_intent(self, text: str) -> tuple[str | None, float]:
        cleaned = normalize_text(text)
        if not cleaned:
            return None, 0.0
        vector = self.vectorizer.transform([cleaned])
        similarities = cosine_similarity(vector, self.pattern_matrix)[0]
        best_score = float(similarities.max())
        if best_score == 0:
            return None, 0.0
        return str(self.classifier.predict(vector)[0]), best_score

    def local_response(self, text: str) -> str:
        cleaned = normalize_text(text)
        if not cleaned:
            return "Please type a question so I can try to help."
        tag, score = self.predict_intent(cleaned)
        user_terms = set(tokenize(cleaned)) - STOP_WORDS
        overlap = any(user_terms.intersection(tokenize(pattern)) for pattern in self.patterns)
        if tag is None or score < 0.24 or not overlap:
            return (
                "I couldn't confidently match that question to my local NLP examples. "
                "Try rephrasing it, ask about a known topic, or configure Groq for broader answers."
            )
        return random.choice(self.responses[tag])


def groq_response(text: str, history: list[dict[str, str]] | None = None) -> str | None:
    """Ask Groq using a key supplied through the environment; never store the key."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    messages = [{
        "role": "system",
        "content": (
            "You are CampusBot, a helpful educational chatbot for a college student. "
            "Answer clearly and accurately, explain concepts step by step when useful, "
            "include small examples for programming questions, handle spelling mistakes, "
            "and admit uncertainty. Keep the answer focused on the user's question."
        )
    }]
    for item in (history or [])[-6:]:
        if item.get("user") and item.get("bot"):
            messages.append({"role": "user", "content": item["user"][:1500]})
            messages.append({"role": "assistant", "content": item["bot"][:2500]})
    messages.append({"role": "user", "content": text[:4000]})
    payload = json.dumps({
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_completion_tokens": 1200
    }).encode("utf-8")
    request = Request(
        GROQ_URL, data=payload, method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    )
    try:
        with urlopen(request, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data["choices"][0]["message"]["content"]
        return answer.strip() if isinstance(answer, str) and answer.strip() else None
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError):
        return None


_bot: NLPChatbot | None = None


def generate_response(text: str, history: list[dict[str, str]] | None = None) -> str:
    """Prefer Groq when configured; otherwise use the local NLP model."""
    global _bot
    if not normalize_text(text):
        return "Please type a question so I can try to help."
    if os.getenv("GROQ_API_KEY", "").strip():
        answer = groq_response(text, history)
        if answer:
            return answer
        # A provider error should not crash the GUI; try the local NLP answer.
    if _bot is None:
        _bot = NLPChatbot()
    return _bot.local_response(text)


def append_chat(user_message: str, bot_message: str) -> None:
    """Append a conversation turn to a local CSV file."""
    exists = HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0
    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user": user_message, "bot": bot_message
        })


def read_history() -> list[dict[str, str]]:
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def run_gui() -> None:
    """Launch the Tkinter desktop interface; network calls run off the UI thread."""
    import tkinter as tk
    from tkinter import scrolledtext

    class CampusBotGUI:
        def __init__(self, root: tk.Tk):
            self.root = root
            self.history: list[dict[str, str]] = []
            self.results: queue.Queue = queue.Queue()
            self.busy = False
            root.title("CampusBot - Python and NLP Chatbot")
            root.geometry("820x640")
            root.minsize(540, 420)
            root.configure(bg="#f3f5f9")

            header = tk.Frame(root, bg="#18243a", padx=18, pady=14)
            header.pack(fill="x")
            tk.Label(header, text="CampusBot", font=("Segoe UI", 20, "bold"),
                     fg="white", bg="#18243a").pack(anchor="w")
            tk.Label(header, text="Python • Natural Language Processing",
                     font=("Segoe UI", 10), fg="#d5dfef", bg="#18243a").pack(anchor="w")

            self.chat = scrolledtext.ScrolledText(
                root, wrap="word", font=("Segoe UI", 11), state="disabled",
                padx=12, pady=12, bg="white", relief="flat"
            )
            self.chat.pack(fill="both", expand=True, padx=14, pady=(14, 8))
            self.chat.tag_configure("user", foreground="#185abd", spacing1=8)
            self.chat.tag_configure("bot", foreground="#202938", spacing1=8)

            bottom = tk.Frame(root, bg="#f3f5f9", padx=14, pady=8)
            bottom.pack(fill="x")
            self.entry = tk.Text(bottom, height=3, wrap="word", font=("Segoe UI", 11))
            self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
            self.entry.bind("<Control-Return>", self.send)
            self.entry.bind("<Return>", self.enter_to_send)
            self.send_button = tk.Button(
                bottom, text="Send", command=self.send, width=10,
                bg="#2457c5", fg="white", activebackground="#1745a8",
                relief="flat", padx=10, pady=8
            )
            self.send_button.pack(side="right", anchor="s")

            controls = tk.Frame(root, bg="#f3f5f9", padx=14, pady=0)
            controls.pack(fill="x", pady=(0, 12))
            tk.Button(controls, text="Clear conversation", command=self.clear).pack(side="left")
            tk.Button(controls, text="Show saved history", command=self.show_history).pack(side="left", padx=8)
            mode = "Groq AI enabled" if os.getenv("GROQ_API_KEY") else "Local NLP mode (set GROQ_API_KEY for broader answers)"
            tk.Label(controls, text=mode, bg="#f3f5f9", fg="#5a6472").pack(side="right")
            self.add_message("CampusBot", "Hello! Ask me a question. I use Python and NLP, with optional Groq AI for broader answers.")

        def add_message(self, speaker: str, message: str):
            self.chat.configure(state="normal")
            tag = "user" if speaker == "You" else "bot"
            self.chat.insert("end", f"{speaker}: {message}\n\n", tag)
            self.chat.configure(state="disabled")
            self.chat.see("end")

        def enter_to_send(self, event):
            if event.state & 0x4:
                return self.send()
            return "break"

        def send(self, event=None):
            if self.busy:
                return "break"
            message = self.entry.get("1.0", "end").strip()
            if not message:
                return "break"
            self.entry.delete("1.0", "end")
            self.add_message("You", message)
            self.busy = True
            self.send_button.configure(state="disabled", text="Thinking…")
            threading.Thread(target=self.answer_worker, args=(message,), daemon=True).start()
            self.root.after(100, self.check_results)
            return "break"

        def answer_worker(self, message: str):
            answer = generate_response(message, self.history)
            self.results.put((message, answer))

        def check_results(self):
            try:
                message, answer = self.results.get_nowait()
            except queue.Empty:
                if self.busy:
                    self.root.after(100, self.check_results)
                return
            self.history.append({"user": message, "bot": answer})
            self.history = self.history[-6:]
            append_chat(message, answer)
            self.add_message("CampusBot", answer)
            self.busy = False
            self.send_button.configure(state="normal", text="Send")

        def clear(self):
            self.history.clear()
            self.chat.configure(state="normal")
            self.chat.delete("1.0", "end")
            self.chat.configure(state="disabled")
            self.add_message("CampusBot", "Conversation cleared. What would you like to ask?")

        def show_history(self):
            rows = read_history()
            self.add_message("CampusBot", "No saved messages yet." if not rows else
                "Recent saved history:\n" + "\n".join(
                    f"You: {row['user']}\nCampusBot: {row['bot']}" for row in rows[-10:]
                ))

    root = tk.Tk()
    CampusBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
