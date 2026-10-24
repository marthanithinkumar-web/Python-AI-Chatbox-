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
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

APP_NAME = "CampusBot"
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
BACKEND_URL = os.getenv("CAMPUSBOT_BACKEND_URL", "https://campusbot-ai-backend.onrender.com").strip()
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
HISTORY_FILE = Path(__file__).with_name("chat_history.csv")
HISTORY_FIELDS = ["timestamp", "user", "bot"]

SYSTEM_INSTRUCTION = """You are CampusBot, a careful, capable, friendly AI assistant for a college student.
Understand the actual question, context, constraints, and requested output. Use earlier messages for
follow-up questions. Ask one concise clarification only when ambiguity changes the answer; otherwise
state a reasonable assumption. Answer all parts of multi-part requests. Start with the direct answer.
Explain unfamiliar terms with examples when helpful. For code, give runnable, consistent solutions.
Never invent facts, numbers, citations, dates, fees, college policies, or live status. State uncertainty
and recommend authoritative sources for changing information. Never claim to have browsed, tested,
or executed something unless that actually happened. Do not ask for passwords, API keys, payment
credentials, or unnecessary sensitive information. You are not an official college service."""

OFFLINE_RESPONSES = {
    "greeting": "Hi! I'm CampusBot. Configure GEMINI_API_KEY to enable flexible AI answers.",
    "help": "Ask a question in your own words. Commands: help, clear, history, exit.",
    "thanks": "You're welcome! What would you like to explore next?",
    "about": "I'm CampusBot, a Python chatbot with a Tkinter desktop interface and optional Gemini AI.",
}
OFFLINE_FALLBACK = (
    "Live AI is unavailable right now. Check your internet connection and try again later."
)


# -------------------- Lightweight NLP helpers --------------------
def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def classify_intent(text: str) -> str | None:
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



# -------------------- Local CSV history --------------------
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


# -------------------- Gemini response engine --------------------
def generate_response(text: str, history: list[dict[str, str]] | None = None,
                      timeout: int = 60) -> str:
    # Shared backend means classmates do not need to create or configure API keys.
    if BACKEND_URL:
        payload = {"message": text[:12000], "history": (history or [])[-8:]}
        request = urllib.request.Request(
            BACKEND_URL.rstrip("/") + "/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data.get("reply", "")
            return answer.strip() if isinstance(answer, str) and answer.strip() else "CampusBot's AI service returned an empty answer. Please try again."
        except urllib.error.HTTPError as exc:
            try:
                data = json.loads(exc.read().decode("utf-8", errors="replace"))
                detail = data.get("error", "")
            except (ValueError, AttributeError):
                detail = ""
            return detail or f"CampusBot AI service returned HTTP {exc.code}. Please try again."
        except (urllib.error.URLError, TimeoutError, OSError):
            return "Couldn't reach CampusBot's shared AI service. Check your internet connection or try again later."
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return "CampusBot's shared AI service returned an unexpected response. Please try again."

    # Optional direct-key mode remains available for the project owner/development.
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return OFFLINE_RESPONSES.get(classify_intent(text), OFFLINE_FALLBACK)
    turns = []
    for item in (history or [])[-12:]:
        role, content = item.get("role"), item.get("content", "")
        if role in {"user", "model"} and isinstance(content, str) and content.strip():
            turns.append({"role": role, "parts": [{"text": content[:12000]}]})
    turns.append({"role": "user", "parts": [{"text": text[:12000]}]})
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": turns,
        "generationConfig": {"temperature": 0.35, "topP": 0.9, "maxOutputTokens": 4096},
    }
    url = API_URL.format(model=MODEL) + "?key=" + api_key
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        candidates = data.get("candidates", [])
        if not candidates:
            reason = data.get("promptFeedback", {}).get("blockReason")
            return (f"The AI provider blocked this request ({reason}). Please rephrase."
                    if reason else "The AI provider returned no answer. Please try again.")
        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        answer = "\n".join(p.get("text", "") for p in parts if p.get("text"))
        if answer.strip():
            return answer.strip()
        reason = candidate.get("finishReason", "")
        return (f"The AI response ended without readable text ({reason}). Please try again."
                if reason else "I couldn't form a useful response. Could you rephrase?")
    except urllib.error.HTTPError as exc:
        if exc.code in (400, 401, 403):
            return "Gemini rejected the request or API key. Check the key, API access, and model name."
        if exc.code == 404:
            return f"Gemini model '{MODEL}' is unavailable to this key. Set GEMINI_MODEL to an available model."
        if exc.code == 429:
            return "Gemini quota or rate limit reached. Wait and try again or check Google AI Studio quota."
        return f"Gemini returned HTTP {exc.code}. Please try again later."
    except (urllib.error.URLError, TimeoutError, OSError):
        return "Couldn't reach Gemini. Check the internet connection and try again."
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return "Gemini returned an unexpected response. Please try again."

def add_turn(history: list[dict[str, str]], user: str, bot: str) -> list[dict[str, str]]:
    return [*history, {"role": "user", "content": user},
            {"role": "model", "content": bot}][-12:]


# -------------------- Tkinter desktop interface --------------------
def run_gui() -> None:
    import tkinter as tk
    from tkinter import scrolledtext
    from tkinter import messagebox

    class CampusBotGUI:
        def __init__(self, root: tk.Tk):
            self.root = root
            root.title("CampusBot — AI Chatbot")
            root.geometry("850x680")
            root.minsize(560, 460)
            root.configure(bg="#f3f5f9")
            self.history: list[dict[str, str]] = []
            self.results: queue.Queue = queue.Queue()
            self.busy = False

            header = tk.Frame(root, bg="#18243a", padx=22, pady=16)
            header.pack(fill="x")
            tk.Label(header, text="CampusBot", font=("Segoe UI", 20, "bold"),
                     fg="white", bg="#18243a").pack(anchor="w")
            mode = "Shared AI service" if BACKEND_URL else ("Live Gemini AI" if os.getenv("GEMINI_API_KEY", "").strip() else "Limited offline mode")
            self.status = tk.Label(header, text=f"{mode} • Ready", font=("Segoe UI", 10),
                                   fg="#cbd5e1", bg="#18243a")
            self.status.pack(anchor="w", pady=(3, 0))

            body = tk.Frame(root, bg="#f3f5f9", padx=18, pady=14)
            body.pack(fill="both", expand=True)
            self.chat = scrolledtext.ScrolledText(
                body, wrap="word", state="disabled", font=("Segoe UI", 11),
                padx=14, pady=12, bg="white", fg="#172033", relief="flat", borderwidth=0)
            self.chat.pack(fill="both", expand=True)
            self.chat.tag_config("system", foreground="#64748b", spacing1=5, spacing3=8)
            self.chat.tag_config("you", foreground="#2459a9", font=("Segoe UI", 10, "bold"), spacing1=8)
            self.chat.tag_config("bot", foreground="#172033", font=("Segoe UI", 10, "bold"), spacing1=8)
            self.chat.tag_config("answer", foreground="#172033", lmargin1=8, lmargin2=8, spacing3=8)
            self.write("CampusBot", "Hi! Ask a question below. Follow-ups use this conversation. "
                       "Answered messages are saved locally.", "system")

            compose = tk.Frame(root, bg="#f3f5f9", padx=18, pady=(0, 14))
            compose.pack(fill="x")
            self.entry = tk.Entry(compose, font=("Segoe UI", 11), relief="solid", bd=1)
            self.entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
            self.entry.bind("<Return>", self.send_event)
            self.send_button = tk.Button(compose, text="Send", command=self.send,
                                         bg="#2459a9", fg="white", relief="flat",
                                         padx=18, pady=9, cursor="hand2")
            self.send_button.pack(side="left")

            controls = tk.Frame(root, bg="#f3f5f9", padx=18, pady=(0, 14))
            controls.pack(fill="x")
            tk.Button(controls, text="Clear conversation", command=self.clear,
                      relief="flat", cursor="hand2").pack(side="left")
            tk.Button(controls, text="Show saved history", command=self.show_history,
                      relief="flat", cursor="hand2").pack(side="left", padx=(8, 0))
            tk.Label(controls, text="Don't enter passwords or API keys.",
                     bg="#f3f5f9", fg="#64748b", font=("Segoe UI", 9)).pack(side="right")
            self.entry.focus_set()
            root.protocol("WM_DELETE_WINDOW", self.close)
            root.after(100, self.poll)

        def write(self, speaker: str, message: str, tag: str) -> None:
            self.chat.configure(state="normal")
            self.chat.insert("end", speaker + "\n", tag if tag in {"system", "you", "bot"} else "system")
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
            command = message.casefold()
            if command in {"exit", "quit", "bye", "goodbye"}:
                self.write("CampusBot", "Goodbye! You can close this window.", "system")
                self.entry.delete(0, "end")
                return
            if command == "help":
                self.write("CampusBot", "Ask a question. Press Enter or Send. Use Clear conversation "
                           "to reset context, or Show saved history to review saved turns.", "system")
                self.entry.delete(0, "end")
                return
            if command == "clear":
                self.clear()
                self.entry.delete(0, "end")
                return
            if command == "history":
                self.show_history()
                self.entry.delete(0, "end")
                return
            self.entry.delete(0, "end")
            self.write("You", message, "you")
            self.busy = True
            self.send_button.configure(state="disabled")
            self.status.configure(text="Thinking…")
            threading.Thread(target=self.generate_in_background,
                             args=(message, list(self.history)), daemon=True).start()

        def generate_in_background(self, message: str, previous: list[dict[str, str]]) -> None:
            try:
                reply = generate_response(message, previous)
                append_chat(message, reply)
                self.results.put(("ok", reply, add_turn(previous, message, reply)))
            except Exception as exc:
                self.results.put(("error", f"Unexpected application error: {exc}", previous))

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
                    mode = "Shared AI service" if BACKEND_URL else ("Live Gemini AI" if os.getenv("GEMINI_API_KEY", "").strip() else "Limited offline mode")
                    self.status.configure(text=f"{mode} • Ready")
                    self.entry.focus_set()
            except queue.Empty:
                pass
            self.root.after(100, self.poll)

        def clear(self) -> None:
            if self.busy:
                self.write("CampusBot", "Please wait for the current answer before clearing context.", "system")
                return
            self.history.clear()
            self.chat.configure(state="normal")
            self.chat.delete("1.0", "end")
            self.chat.configure(state="disabled")
            self.write("CampusBot", "Conversation context cleared. Saved CSV history remains available.", "system")
            self.status.configure(text="Conversation cleared")

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
            if self.busy and not messagebox.askyesno("CampusBot", "An answer is still being generated. Close anyway?"):
                return
            root.destroy()

    root = tk.Tk()
    CampusBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        run_gui()
    except ImportError as exc:
        raise SystemExit(f"Tkinter is unavailable. Repair Python with Tcl/Tk enabled. Details: {exc}")
