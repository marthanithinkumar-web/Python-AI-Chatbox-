"""CampusBot: a conversational Python chatbot with optional live Gemini AI."""
from nlp_engine import generate_response
from storage import append_chat, read_history


def count_words(text: str) -> int:
    """Count words recursively (Python lab demonstration)."""
    words = text.split()
    def count(items):
        return 0 if not items else 1 + count(items[1:])
    return count(words)


def get_non_empty_input(prompt="You: "):
    while True:
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCampusBot: Session closed. Goodbye!")
            raise SystemExit(0)
        if value:
            return value
        print("CampusBot: Please type a message before pressing Enter.")


def run_chat():
    import os
    live = bool(os.getenv("GEMINI_API_KEY", "").strip())
    print("\n" + "=" * 60)
    print(" CAMPUSBOT — Conversational AI Chatbot")
    print("=" * 60)
    print("Mode: " + ("Live Gemini AI" if live else "Limited offline mode (configure GEMINI_API_KEY for AI)"))
    print("Ask general questions. Commands: help, clear, history, exit.")
    print("Do not enter passwords, API keys, or confidential information.\n")
    history = []
    while True:
        message = get_non_empty_input()
        command = message.casefold()
        if command in {"exit", "quit", "bye", "goodbye"}:
            reply = "Goodbye! Thanks for chatting with CampusBot."
            print(f"CampusBot: {reply}")
            append_chat(message, reply)
            break
        if command == "clear":
            history.clear()
            print("CampusBot: Conversation context cleared.\n")
            continue
        if command == "history":
            rows = read_history()
            if not rows:
                print("CampusBot: No saved chat history yet.\n")
            else:
                print("\n--- Recent saved turns ---")
                for row in rows[-10:]:
                    print(f"You: {row['user']}\nCampusBot: {row['bot']}\n")
            continue
        if command == "help":
            print("CampusBot: Ask about almost any topic. With Gemini enabled, I can answer follow-up questions using this conversation. Commands: clear (reset context), history (show saved turns), exit (quit).\n")
            continue
        print("CampusBot: Thinking...\n")
        reply = generate_response(message, history=history)
        print(f"CampusBot: {reply}\n")
        history.extend([{"role": "user", "content": message}, {"role": "model", "content": reply}])
        history = history[-12:]
        append_chat(message, reply)


if __name__ == "__main__":
    run_chat()
