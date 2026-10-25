"""CampusBot: an offline desktop chatbot using classical NLP.

The chatbot trains a TF-IDF + Logistic Regression intent classifier from
intents.json at startup. It does not call Groq, another hosted model, or any
external API. Install requirements once; chatting then works offline.
"""
from __future__ import annotations

import csv
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

APP_NAME = "CampusBot"
BASE_DIR = Path(__file__).resolve().parent
INTENTS_FILE = BASE_DIR / "intents.json"
HISTORY_FILE = BASE_DIR / "chat_history.csv"
HISTORY_FIELDS = ["timestamp", "user", "bot"]

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as exc:
    raise SystemExit(
        "CampusBot needs scikit-learn. Install it with: python -m pip install -r requirements.txt"
    ) from exc


def normalize_text(text: str) -> str:
    """Normalize text for the intent matcher while preserving useful words."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    """Simple word tokenizer used for transparent NLP preprocessing."""
    return re.findall(r"[a-z0-9']+", normalize_text(text))


class NLPChatbot:
    """Intent-based chatbot trained locally with TF-IDF and Logistic Regression."""

    def __init__(self, intents_path: Path | str = INTENTS_FILE):
        self.intents_path = Path(intents_path)
        self.intents = self._load_intents()
        self.patterns: list[str] = []
        self.labels: list[str] = []
        self.label_to_intent: dict[str, dict] = {}
        for intent in self.intents:
            tag = intent["tag"]
            self.label_to_intent[tag] = intent
            for pattern in intent.get("patterns", []):
                cleaned = normalize_text(pattern)
                if cleaned:
                    self.patterns.append(cleaned)
                    self.labels.append(tag)
        if not self.patterns:
            raise ValueError("intents.json must contain at least one non-empty pattern.")
        self.vectorizer = TfidfVectorizer(
            tokenizer=tokenize, token_pattern=None, lowercase=False,
            ngram_range=(1, 2), sublinear_tf=True,
        )
        self.pattern_matrix = self.vectorizer.fit_transform(self.patterns)
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        self.classifier.fit(self.pattern_matrix, self.labels)

    def _load_intents(self) -> list[dict]:
        with self.intents_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        intents = data.get("intents") if isinstance(data, dict) else None
        if not isinstance(intents, list):
            raise ValueError("intents.json must contain an 'intents' list.")
        for item in intents:
            if not isinstance(item, dict) or not item.get("tag"):
                raise ValueError("Each intent must have a tag.")
            if not item.get("patterns") or not item.get("responses"):
                raise ValueError(f"Intent {item.get('tag', '?')} needs patterns and responses.")
        return intents

    def predict_intent(self, text: str) -> tuple[str | None, float, float]:
        cleaned = normalize_text(text)
        if not cleaned:
            return None, 0.0, 0.0
        vector = self.vectorizer.transform([cleaned])
        scores = cosine_similarity(vector, self.pattern_matrix)[0]
        best_index = int(scores.argmax())
        similarity = float(scores[best_index])
        if not similarity:
            return None, 0.0, 0.0
        predicted = str(self.classifier.predict(vector)[0])
        return predicted, similarity, float(scores[best_index])

    def respond(self, text: str) -> str:
        cleaned = normalize_text(text)
        if not cleaned:
            return "Please type a question so I can try to help."
        tag, similarity, _ = self.predict_intent(cleaned)
        # Threshold prevents unrelated questions from being confidently misclassified.
        if tag is None or similarity < 0.16:
            return (
                "I'm not confident I understood that yet. Try rephrasing your question, "
                "or add more examples to intents.json so I can learn that topic."
            )
        intent = self.label_to_intent[tag]
        return random.choice(intent["responses"])


_chatbot: NLPChatbot | None = None


def generate_response(text: str, history: list[dict[str, str]] | None = None) -> str:
    """Public response function retained for the GUI and tests."""
    global _chatbot
    if _chatbot is None:
        _chatbot = NLPChatbot()
    return _chatbot.respond(text)


def append_chat(user_message: str, bot_message: str) -> None:
    exists = HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0
    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user": user_message,
            "bot": bot_message,
        })


def read_history() -> list[dict[str, str]]:
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def run_gui() -> None:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext
    import threading
    import queue

    class CampusBotGUI:
        def __init__(self, root: tk.Tk):
            self.root = root
            root.title("CampusBot - Python + NLP Chatbot")
            root.geometry("850x680")
            root.minsize(560, 460)
            root.configure(bg="#f3f5f9")
            self.results: queue.Queue = queue.Queue()
            self.busy = False

            header = tk.Frame(root, bg="#18243a", padx=22, pady=16)
            header.pack(fill="x")
            tk.Label(header, text="CampusBot", font=("Segoe UI", 20, "bold"),
                     fg="white", bg="#18243a").pack(anchor="w")
            self.status = tk.Label(
                header, text="Local NLP engine • Offline ready",
                font=("Segoe UI", 10), fg="#cbd5e1", bg="#18243a")
            self.status.pack(anchor="w", pady=(3, 0))

            body = tk.Frame(root, bg="#f3f5f9", padx=18, pady=14)
            body.pack(fill="both", expand=True)
            self.chat = scrolledtext.ScrolledText(
                body, wrap="word", state="disabled", font=("Segoe UI", 11),
                padx=14, pady=12, bg="white", fg="#172033", relief="flat", borderwidth=0)
            self.chat.pack(fill="both", expand=True)
            self.chat.tag_config("system", foreground="#64748b", spacing1=5, spacing3=8)
            self.chat.tag_config("you", foreground="#2459a9",
                                 font=("Segoe UI", 10, "bold"), spacing1=8)
            self.chat.tag_config("bot", foreground="#172033",
                                 font=("Segoe UI", 10, "bold"), spacing1=8)
            self.chat.tag_config("answer", foreground="#172033",
                                 lmargin1=8, lmargin2=8, spacing3=8)
            self.write("CampusBot", "Hi! I'm an offline NLP chatbot. Ask me about Python, NLP, "
                       "college study tips, or the project. My answers come from local intent examples.",
                       "system")

            compose = tk.Frame(root, bg="#f3f5f9", padx=18)
            compose.pack(fill="x", pady=(0, 14))
            self.entry = tk.Entry(compose, font=("Segoe UI", 11), relief="solid", bd=1)
            self.entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
            self.entry.bind("<Return>", self.send_event)
            self.send_button = tk.Button(
                compose, text="Send", command=self.send, bg="#2459a9", fg="white",
                relief="flat", padx=18, pady=9, cursor="hand2")
            self.send_button.pack(side="left")

            controls = tk.Frame(root, bg="#f3f5f9", padx=18)
            controls.pack(fill="x", pady=(0, 14))
            tk.Button(controls, text="Clear conversation", command=self.clear,
                      relief="flat", cursor="hand2").pack(side="left")
            tk.Button(controls, text="Show saved history", command=self.show_history,
                      relief="flat", cursor="hand2").pack(side="left", padx=(8, 0))
            tk.Label(controls, text="Local processing • No API key required",
                     bg="#f3f5f9", fg="#64748b", font=("Segoe UI", 9)).pack(side="right")
            self.entry.focus_set()
            root.protocol("WM_DELETE_WINDOW", self.close)
            root.after(100, self.poll)

        def write(self, speaker: str, message: str, tag: str) -> None:
            self.chat.configure(state="normal")
            self.chat.insert("end", speaker + "\n",
                             tag if tag in {"system", "you", "bot"} else "system")
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
            self.status.configure(text="Processing locally…")
            threading.Thread(target=self.generate_in_background, args=(message,), daemon=True).start()

        def generate_in_background(self, message: str) -> None:
            try:
                reply = generate_response(message)
                try:
                    append_chat(message, reply)
                except OSError:
                    pass
                self.results.put(("ok", reply))
            except Exception:
                self.results.put(("error", "I couldn't process that message. Check that intents.json is present and valid."))

        def poll(self) -> None:
            try:
                while True:
                    kind, reply = self.results.get_nowait()
                    self.write("CampusBot", reply, "bot" if kind == "ok" else "system")
                    self.busy = False
                    self.send_button.configure(state="normal")
                    self.status.configure(text="Local NLP engine • Ready")
                    self.entry.focus_set()
            except queue.Empty:
                pass
            self.root.after(100, self.poll)

        def clear(self) -> None:
            self.chat.configure(state="normal")
            self.chat.delete("1.0", "end")
            self.chat.configure(state="disabled")
            self.write("CampusBot", "Conversation display cleared. Saved CSV history remains available.", "system")

        def show_history(self) -> None:
            rows = read_history()
            if not rows:
                self.write("CampusBot", "No saved chat history yet.", "system")
                return
            self.write("CampusBot", f"Showing the latest {min(10, len(rows))} saved turns:", "system")
            for row in rows[-10:]:
                self.write("You", row.get("user", ""), "you")
                self.write("CampusBot", row.get("bot", ""), "bot")

        def close(self) -> None:
            if self.busy and not messagebox.askyesno(
                "CampusBot", "A reply is still being generated. Close anyway?"
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
        raise SystemExit(f"Tkinter is unavailable. Repair Python with Tcl/Tk enabled. Details: {exc}") from exc
