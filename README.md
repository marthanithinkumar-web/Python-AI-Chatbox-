# CampusBot — Python and NLP Chatbot

CampusBot is a single-file desktop chatbot project built mainly to demonstrate Python programming and Natural Language Processing (NLP).

## Main features
- Text normalization and tokenization
- TF-IDF text vectorization (unigrams and bigrams)
- Logistic Regression intent classification
- Cosine-similarity check and a cautious unknown-question fallback
- Tkinter desktop interface
- CSV chat history
- Optional Groq-generated answers for broader questions
- Local NLP responses remain available if Groq is not configured or is unavailable

## Requirements
- Python 3.10+
- scikit-learn
- Tkinter (normally included with Windows Python)

## Run on Windows
1. Install Python and select the option to add Python to PATH.
2. Open Command Prompt or PowerShell in this repository folder.
3. Install the dependency: python -m pip install -r requirements.txt
4. Start the app: python CampusBot.py

You can also double-click run_gui.bat.

## Optional Groq mode
The project is designed to work locally without an API key. To enable broader online answers, set GROQ_API_KEY in your environment before starting the app. Never paste the key into CampusBot.py or commit it to GitHub.

PowerShell (current terminal only):
$env:GROQ_API_KEY="your-key-here"
python CampusBot.py

The default model is openai/gpt-oss-120b. If needed, set GROQ_MODEL to another model available to your Groq account. Online answers require internet access and depend on provider availability and quota. When the request fails, CampusBot tries its local NLP response instead.

## Project structure
- CampusBot.py — application, embedded training examples, NLP pipeline, GUI, optional Groq call, and CSV history
- requirements.txt — required Python package
- tests/test_campusbot.py — automated tests
- run_gui.bat — Windows launch helper
- run_tests.bat — Windows test helper
- PROJECT_REPORT.md — report focused on Python and NLP

## Tests
Run:
python -m unittest discover -s tests -v

The local NLP pipeline is educational and has limited coverage because its training set is intentionally compact. Optional generated answers can be wrong; verify important information.
