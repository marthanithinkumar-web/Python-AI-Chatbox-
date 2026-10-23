"""CSV persistence for local CampusBot conversation history."""
import csv
from datetime import datetime, timezone
from pathlib import Path

HISTORY_FILE = Path(__file__).with_name("chat_history.csv")
FIELDS = ["timestamp", "user", "bot"]


def append_chat(user_message: str, bot_message: str) -> None:
    exists = HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0
    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user": user_message, "bot": bot_message,
        })


def read_history() -> list[dict[str, str]]:
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
