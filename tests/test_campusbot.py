import csv
import importlib.util
import json
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


class NLPChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bot = campusbot.NLPChatbot()

    def test_normalize_text(self):
        self.assertEqual(campusbot.normalize_text("  HELLO, Python!! "), "hello python")

    def test_tokenize(self):
        self.assertEqual(campusbot.tokenize("Hello, NLP 101!"), ["hello", "nlp", "101"])

    def test_known_python_intent(self):
        tag, similarity, _ = self.bot.predict_intent("what is python")
        self.assertEqual(tag, "python_definition")
        self.assertGreater(similarity, 0.15)

    def test_known_nlp_intent(self):
        tag, similarity, _ = self.bot.predict_intent("explain natural language processing")
        self.assertEqual(tag, "nlp_definition")
        self.assertGreater(similarity, 0.15)

    def test_response_for_tokenization(self):
        self.assertIn("token", self.bot.respond("what is tokenization").lower())

    def test_empty_input(self):
        self.assertIn("type a question", self.bot.respond("   ").lower())

    def test_unknown_question_uses_fallback(self):
        self.assertIn("not confident", self.bot.respond("quantum submarine recipes on mars").lower())

    def test_custom_dataset_can_train(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "intents.json"
            path.write_text(json.dumps({"intents": [
                {"tag": "greeting", "patterns": ["hello", "hi there"], "responses": ["Hello!"]},
                {"tag": "farewell", "patterns": ["goodbye", "see you"], "responses": ["Bye!"]}
            ]}), encoding="utf-8")
            bot = campusbot.NLPChatbot(path)
            self.assertEqual(bot.predict_intent("hello")[0], "greeting")

    def test_csv_history(self):
        with tempfile.TemporaryDirectory() as temp:
            history_path = Path(temp) / "chat_history.csv"
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
