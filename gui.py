"""CampusBot desktop GUI built with Tkinter; shares the existing Gemini engine and CSV history."""
from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext
from typing import Callable

from nlp_engine import generate_response
from storage import append_chat, read_history


def respond_to_message(
    message: str,
    history: list[dict[str, str]],
    response_generator: Callable[..., str] | None = None,
) -> tuple[str, list[dict[str, str]]]:
    """Generate, persist, and return a reply plus updated in-memory context."""
    generator = response_generator or generate_response
    reply = generator(message, history=history)
    append_chat(message, reply)
    updated = [*history, {"role": "user", "content": message},
               {"role": "model", "content": reply}]
    return reply, updated[-12:]


class CampusBotGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CampusBot — AI Chatbot")
        self.root.geometry("850x680")
        self.root.minsize(560, 460)
        self.history: list[dict[str, str]] = []
        self.results: queue.Queue = queue.Queue()
        self.busy = False

        root.configure(bg="#f3f5f9")
        header = tk.Frame(root, bg="#18243a", padx=22, pady=16)
        header.pack(fill="x")
        tk.Label(
            header, text="CampusBot", font=("Segoe UI", 20, "bold"),
            fg="white", bg="#18243a"
        ).pack(anchor="w")
        mode = "Live Gemini AI" if os.getenv("GEMINI_API_KEY", "").strip() else "Limited offline mode"
        self.status = tk.Label(
            header, text=f"{mode}  •  Ready", font=("Segoe UI", 10),
            fg="#cbd5e1", bg="#18243a"
        )
        self.status.pack(anchor="w", pady=(3, 0))

        body = tk.Frame(root, bg="#f3f5f9", padx=18, pady=14)
        body.pack(fill="both", expand=True)
        self.chat = scrolledtext.ScrolledText(
            body, wrap="word", state="disabled", font=("Segoe UI", 11),
            padx=14, pady=12, bg="white", fg="#172033", relief="flat",
            borderwidth=0
        )
        self.chat.pack(fill="both", expand=True)
        self.chat.tag_config("system", foreground="#64748b", spacing1=5, spacing3=8)
        self.chat.tag_config("you", foreground="#2459a9", font=("Segoe UI", 10, "bold"), spacing1=8)
        self.chat.tag_config("bot", foreground="#172033", font=("Segoe UI", 10, "bold"), spacing1=8)
        self.chat.tag_config("answer", foreground="#172033", lmargin1=8, lmargin2=8, spacing3=8)
        self._write("CampusBot", "Hi! Ask a question below. Follow-ups use the current conversation. Your messages and replies are saved locally.", "system")

        compose = tk.Frame(root, bg="#f3f5f9", padx=18, pady=(0, 14))
        compose.pack(fill="x")
        self.entry = tk.Entry(
            compose, font=("Segoe UI", 11), relief="solid", bd=1,
            highlightthickness=1, highlightbackground="#d5dbe5"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self.entry.bind("<Return>", self._send_event)
        self.send_button = tk.Button(
            compose, text="Send", command=self.send_message, bg="#2459a9",
            fg="white", activebackground="#1c478a", activeforeground="white",
            relief="flat", padx=18, pady=9, cursor="hand2"
        )
        self.send_button.pack(side="left")

        controls = tk.Frame(root, bg="#f3f5f9", padx=18, pady=(0, 14))
        controls.pack(fill="x")
        tk.Button(controls, text="Clear conversation", command=self.clear_context,
                  relief="flat", cursor="hand2").pack(side="left")
        tk.Button(controls, text="Show saved history", command=self.show_history,
                  relief="flat", cursor="hand2").pack(side="left", padx=(8, 0))
        tk.Label(
            controls, text="Don't enter passwords or API keys.",
            bg="#f3f5f9", fg="#64748b", font=("Segoe UI", 9)
        ).pack(side="right")
        self.entry.focus_set()
        self.root.after(100, self._poll_results)

    def _write(self, speaker: str, message: str, tag: str) -> None:
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{speaker}\n", tag if tag in {"system", "you", "bot"} else "system")
        self.chat.insert("end", f"{message}\n\n", "answer")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _send_event(self, _event=None):
        self.send_message()
        return "break"

    def send_message(self) -> None:
        message = self.entry.get().strip()
        if not message or self.busy:
            return
        command = message.casefold()
        if command in {"exit", "quit", "bye", "goodbye"}:
            self._write("CampusBot", "Goodbye! You can close this window.", "system")
            self.entry.delete(0, "end")
            return
        if command == "help":
            self._write("CampusBot", "Ask a question in your own words. Press Enter or Send. Use Clear conversation to reset context, or Show saved history to review local CSV history.", "system")
            self.entry.delete(0, "end")
            return
        if command == "clear":
            self.clear_context()
            self.entry.delete(0, "end")
            return
        if command == "history":
            self.show_history()
            self.entry.delete(0, "end")
            return
        self.entry.delete(0, "end")
        self._write("You", message, "you")
        self.busy = True
        self.send_button.configure(state="disabled")
        self.status.configure(text="Thinking…")
        prior_history = list(self.history)
        threading.Thread(
            target=self._generate_in_background,
            args=(message, prior_history),
            daemon=True
        ).start()

    def _generate_in_background(self, message: str, prior_history: list[dict[str, str]]) -> None:
        try:
            reply, updated_history = respond_to_message(message, prior_history)
            self.results.put(("ok", reply, updated_history))
        except Exception as exc:
            self.results.put(("error", f"Unexpected application error: {exc}", prior_history))

    def _poll_results(self) -> None:
        try:
            while True:
                kind, reply, updated_history = self.results.get_nowait()
                if kind == "ok":
                    self.history = updated_history
                    self._write("CampusBot", reply, "bot")
                else:
                    self._write("CampusBot", reply, "system")
                self.busy = False
                self.send_button.configure(state="normal")
                mode = "Live Gemini AI" if os.getenv("GEMINI_API_KEY", "").strip() else "Limited offline mode"
                self.status.configure(text=f"{mode}  •  Ready")
                self.entry.focus_set()
        except queue.Empty:
            pass
        self.root.after(100, self._poll_results)

    def clear_context(self) -> None:
        if self.busy:
            self._write("CampusBot", "Please wait for the current answer before clearing the conversation.", "system")
            return
        self.history.clear()
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self._write("CampusBot", "Conversation context cleared. Your saved CSV history remains available.", "system")
        self.status.configure(text="Conversation cleared")

    def show_history(self) -> None:
        rows = read_history()
        if not rows:
            self._write("CampusBot", "No saved chat history yet.", "system")
            return
        self._write("CampusBot", f"Showing the latest {min(10, len(rows))} saved turns:", "system")
        for row in rows[-10:]:
            self._write("You", row.get("user", ""), "you")
            self._write("CampusBot", row.get("bot", ""), "bot")


def run_gui() -> None:
    root = tk.Tk()
    CampusBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
