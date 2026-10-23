"""Automated tests for CampusBot. Run: python -m unittest -v"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import nlp_engine
import storage
from main import count_words, get_non_empty_input


class NLPTests(unittest.TestCase):
    def test_tokenization(self):
        self.assertEqual(nlp_engine.tokenize("Hello, CAMPUS! 2026"), ["hello", "campus", "2026"])

    def test_stop_words(self):
        self.assertEqual(nlp_engine.preprocess("What is the exam schedule"), ["exam", "schedule"])

    def test_greeting_intent(self):
        self.assertEqual(nlp_engine.classify_intent("hello there"), "greeting")

    def test_unknown_intent_is_none(self):
        self.assertIsNone(nlp_engine.classify_intent("quantum banana spaceship"))

    def test_no_key_has_honest_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn("GEMINI_API_KEY", nlp_engine.generate_response("Explain black holes"))

    def test_live_ai_parses_response(self):
        fake_response = MagicMock()
        fake_response.__enter__.return_value.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "A black hole is a region of space where gravity is extremely strong."}]}}]
        }).encode()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), patch("nlp_engine.urllib.request.urlopen", return_value=fake_response) as mocked:
            answer = nlp_engine.generate_response(
                "Explain black holes",
                history=[{"role": "user", "content": "What is gravity?"}, {"role": "model", "content": "Gravity is attraction."}]
            )
        self.assertIn("black hole", answer)
        request = mocked.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertIn("understand the meaning", payload["system_instruction"]["parts"][0]["text"])
        self.assertEqual(len(payload["contents"]), 3)
        self.assertEqual(payload["generationConfig"]["temperature"], 0.35)
        self.assertEqual(payload["generationConfig"]["maxOutputTokens"], 4096)

    def test_rate_limit_message(self):
        from urllib.error import HTTPError
        error = HTTPError("url", 429, "quota", {}, None)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), patch("nlp_engine.urllib.request.urlopen", side_effect=error):
            self.assertIn("quota", nlp_engine.generate_response("Tell me something"))

    def test_missing_model_message(self):
        from urllib.error import HTTPError
        error = HTTPError("url", 404, "missing", {}, None)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), patch("nlp_engine.urllib.request.urlopen", side_effect=error):
            self.assertIn("GEMINI_MODEL", nlp_engine.generate_response("Tell me something"))

    def test_empty_text_preprocessing(self):
        self.assertEqual(nlp_engine.preprocess("   "), [])


class AppTests(unittest.TestCase):
    def test_recursive_word_count(self):
        self.assertEqual(count_words("Python is easy"), 3)
        self.assertEqual(count_words(""), 0)

    def test_blank_input_retries(self):
        with patch("builtins.input", side_effect=["  ", "hello"]), patch("builtins.print"):
            self.assertEqual(get_non_empty_input(), "hello")

    def test_csv_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "history.csv"
            with patch.object(storage, "HISTORY_FILE", path):
                storage.append_chat("hello, bot", "Hi! Welcome.")
                rows = storage.read_history()
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["user"], "hello, bot")
                self.assertEqual(rows[0]["bot"], "Hi! Welcome.")


if __name__ == "__main__":
    unittest.main()
