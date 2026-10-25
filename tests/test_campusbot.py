import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "CampusBot.py"
SPEC = importlib.util.spec_from_file_location("campusbot", MODULE_PATH)
campusbot = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = campusbot
SPEC.loader.exec_module(campusbot)


class CampusBotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bot = campusbot.NLPChatbot()

    def test_normalize_text(self):
        self.assertEqual(campusbot.normalize_text("  HELLO, Python!! "), "hello python")

    def test_tokenize(self):
        self.assertEqual(campusbot.tokenize("Hello, NLP 101!"), ["hello", "nlp", "101"])

    def test_python_intent(self):
        tag, score = self.bot.predict_intent("what is python")
        self.assertEqual(tag, "python")
        self.assertGreater(score, 0.2)

    def test_nlp_intent(self):
        tag, score = self.bot.predict_intent("explain natural language processing")
        self.assertEqual(tag, "nlp")
        self.assertGreater(score, 0.2)

    def test_local_response_for_known_topic(self):
        self.assertIn("programming language", self.bot.local_response("what is python").lower())

    def test_empty_input(self):
        self.assertIn("type a question", campusbot.generate_response("   ").lower())

    def test_unknown_question_fallback(self):
        answer = self.bot.local_response("quantum submarine recipes on mars")
        self.assertTrue("couldn't confidently" in answer.lower() or "could not confidently" in answer.lower())

    def test_groq_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(campusbot.groq_response("hello"))

    def test_groq_failure_falls_back(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "invalid-test-key"}, clear=True), \
             patch.object(campusbot, "groq_response", return_value=None), \
             patch.object(campusbot, "_bot", self.bot):
            answer = campusbot.generate_response("what is python")
            self.assertIn("programming language", answer.lower())

    def test_csv_history(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "chat_history.csv"
            with patch.object(campusbot, "HISTORY_FILE", path):
                campusbot.append_chat("Question, with comma", "Answer")
                rows = campusbot.read_history()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["user"], "Question, with comma")
            self.assertEqual(rows[0]["bot"], "Answer")


if __name__ == "__main__":
    unittest.main()
