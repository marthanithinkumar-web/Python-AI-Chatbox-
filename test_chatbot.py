"""Run tests with python -m unittest -v."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import nlp_engine
import storage
from main import count_words, get_non_empty_input


class NLPTests(unittest.TestCase):
    def test_tokenization(self):
        self.assertEqual(nlp_engine.tokenize("Hello, CAMPUS! 2026"), ["hello", "campus", "2026"])

    def test_stop_words_and_synonyms(self):
        self.assertEqual(nlp_engine.preprocess("What is the exam schedule"), ["exam", "timetable"])

    def test_exam_intent(self):
        self.assertEqual(nlp_engine.classify_intent("When is the exam date?"), "exam")

    def test_fees_intent(self):
        self.assertEqual(nlp_engine.classify_intent("Tell me about tuition charges"), "fees")

    def test_library_intent(self):
        self.assertEqual(nlp_engine.classify_intent("Can I borrow books?"), "library")

    def test_unknown_fallback(self):
        self.assertEqual(nlp_engine.generate_response("quantum banana spaceship"), nlp_engine.FALLBACK)

    def test_empty_text(self):
        self.assertIsNone(nlp_engine.classify_intent("   "))


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
