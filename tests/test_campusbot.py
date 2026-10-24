import csv
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import urllib.error

MODULE_PATH = Path(__file__).resolve().parents[1] / "CampusBot.py"
SPEC = importlib.util.spec_from_file_location("campusbot", MODULE_PATH)
campusbot = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = campusbot
SPEC.loader.exec_module(campusbot)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


class CampusBotCoreTests(unittest.TestCase):
    def setUp(self):
        self.backend = patch.object(campusbot, "BACKEND_URL", "https://example.test")
        self.backend.start()
        self.addCleanup(self.backend.stop)

    @patch("campusbot.urllib.request.urlopen")
    def test_shared_backend_returns_reply_and_sends_recent_history(self, urlopen):
        urlopen.return_value = FakeResponse({"reply": "Hello from AI"})
        history = [{"role": "user", "content": str(i)} for i in range(10)]

        result = campusbot.generate_response("hello", history)

        self.assertEqual(result, "Hello from AI")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.test/chat")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["message"], "hello")
        self.assertEqual(len(body["history"]), 8)

    @patch("campusbot.urllib.request.urlopen")
    def test_empty_backend_reply_is_handled(self, urlopen):
        urlopen.return_value = FakeResponse({"reply": "   "})
        self.assertIn("empty answer", campusbot.generate_response("hello").lower())

    @patch("campusbot.urllib.request.urlopen")
    def test_http_error_is_reported_without_crashing(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError(
            "https://example.test/chat", 429, "Too Many Requests", {},
            io.BytesIO(b'{"error":"Rate limit reached"}'),
        )
        self.assertEqual(campusbot.generate_response("hello"), "Rate limit reached")

    @patch("campusbot.urllib.request.urlopen")
    def test_network_error_is_friendly(self, urlopen):
        urlopen.side_effect = urllib.error.URLError("offline")
        self.assertIn("couldn't reach", campusbot.generate_response("hello").lower())

    @patch("campusbot.urllib.request.urlopen")
    def test_malformed_json_is_handled(self, urlopen):
        class BadResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b"not-json"

        urlopen.return_value = BadResponse()
        self.assertIn("unexpected response", campusbot.generate_response("hello").lower())

    def test_empty_backend_configuration_fails_gracefully(self):
        with patch.object(campusbot, "BACKEND_URL", ""):
            self.assertIn("not configured", campusbot.generate_response("hello").lower())

    def test_add_turn_keeps_most_recent_twelve_messages(self):
        previous = [{"role": "user", "content": str(i)} for i in range(12)]
        updated = campusbot.add_turn(previous, "new question", "new answer")
        self.assertEqual(len(updated), 12)
        self.assertEqual(updated[-2]["content"], "new question")
        self.assertEqual(updated[-1]["content"], "new answer")

    def test_csv_history_writes_header_and_reads_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "chat_history.csv"
            with patch.object(campusbot, "HISTORY_FILE", history_path):
                campusbot.append_chat("Question, with comma", "Answer")
                campusbot.append_chat("Second", "Response")
                rows = campusbot.read_history()
                with history_path.open(newline="", encoding="utf-8") as handle:
                    header = next(csv.reader(handle))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["user"], "Question, with comma")
            self.assertEqual(rows[1]["bot"], "Response")
            self.assertEqual(header[0], "timestamp")


if __name__ == "__main__":
    unittest.main()
