# CampusBot — Conversational AI Chatbot with Python and NLP

CampusBot now supports a **real generative-AI conversation mode** using Google's Gemini API. It can answer general questions, explain concepts, write code, and handle follow-up questions using recent conversation context. The old fixed-response-only behavior is no longer the main experience.

## Features
- Live AI responses using Gemini (default model: gemini-2.5-flash)
- Conversation context for follow-up questions, with a clear-context command
- System instructions to encourage direct, helpful answers and honest uncertainty
- API errors, quota limits, and network failures handled with readable messages
- API key read from an environment variable; no key committed to Git
- Local CSV history, console chat, and Windows launcher
- Offline fallback if no API key is configured
- Automated unit tests and GitHub Actions

## 1. Requirements
- Python 3.10+
- Internet connection for live AI mode
- A Gemini API key from Google AI Studio: https://aistudio.google.com/app/apikey
- No third-party Python packages are required

## 2. Configure the API key on Windows
Keep your key private. Do not paste it into source code, GitHub commits, screenshots, or chat messages.

**Temporary setup (only for the current PowerShell window):**
1. Open PowerShell in the project folder.
2. Run:
   ```powershell
   $env:GEMINI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
   python main.py
   ```
3. Replace the placeholder locally with your key. Do not commit the command or key.

**Persistent setup for your Windows user:**
1. Open Windows Search and find “Edit environment variables for your account”.
2. Add a user variable named `GEMINI_API_KEY` and set its value to your key.
3. Close and reopen PowerShell, then run `python main.py`.

Optional: set `GEMINI_MODEL` to a model enabled for your API key. Default is `gemini-2.5-flash`.

## 3. Run
- Double-click `run_chatbot.bat`, or run `python main.py` from PowerShell.
- Run tests with `python -m unittest -v` or double-click `run_tests.bat`.
- Type `clear` to clear conversation context, `history` to view local saved turns, and `exit` to quit.

## 4. How it works
The program sends the user message and up to 12 recent user/assistant messages to Gemini. The provider generates the response. The Python project keeps only the recent context in memory for the current session; local CSV history is for review and is not automatically sent to the AI. A system instruction encourages helpful responses and discourages invented current facts.

## 5. Security and limitations
- Your API key is sent to Google's Gemini API over HTTPS and must be protected.
- Do not use a public repository secret or commit your key. Never share credentials in chat.
- API availability, rate limits, model access, and pricing depend on your Google AI Studio account and current terms.
- Without a key, CampusBot is limited to simple built-in replies and cannot provide real generative answers.
- The chatbot may still be wrong; verify important information.
- This is a student project, not an official college service.

## Project structure
- `main.py` — chat loop and commands
- `nlp_engine.py` — Gemini API integration and NLP helpers
- `storage.py` — local CSV history
- `test_chatbot.py` — automated tests
- `PROJECT_REPORT.md` — report draft
- `PROJECT_OUTCOMES.md` — learning outcomes
- `TEST_RESULTS.md` — CI test results
