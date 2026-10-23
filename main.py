"""CampusBot: a beginner-friendly college information chatbot."""
from nlp_engine import generate_response
from storage import append_chat, read_history


def count_words(text: str) -> int:
    """Count words recursively for a Python lab demonstration."""
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
    print("\n" + "=" * 54)
    print(" CAMPUSBOT — Python AI Chatbot Using NLP")
    print("=" * 54)
    print("Ask about courses, exams, attendance, fees, library,")
    print("timetable, contact, or type help / history / exit.\n")
    while True:
        message = get_non_empty_input()
        if message.casefold() in {"exit", "quit", "bye", "goodbye"}:
            reply = "Goodbye! Thank you for chatting with CampusBot."
            print(f"CampusBot: {reply}")
            append_chat(message, reply)
            break
        if message.casefold() == "history":
            rows = read_history()
            if not rows:
                print("CampusBot: No saved chat history yet.")
            else:
                print("\n--- Recent chat history ---")
                for row in rows[-10:]:
                    print(f"You: {row['user']}\nCampusBot: {row['bot']}\n")
            continue
        reply = generate_response(message)
        print(f"CampusBot: {reply}\n")
        append_chat(message, reply)


if __name__ == "__main__":
    run_chat()
