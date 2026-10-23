# CampusBot — Conversational AI Chatbot with Python and NLP

CampusBot supports a **desktop graphical interface built with Python Tkinter** and a console interface. Both share the same Gemini API integration, conversation-context handling, and local CSV history.

## Features
- Desktop chat window with message history, input field, Send button, and Enter-to-send
- Live AI responses using Gemini; model selected through the `GEMINI_MODEL` environment variable
- Conversation context for follow-up questions, with a clear-context control
- Show saved local CSV history from the GUI
- Background API calls so the window stays responsive while Gemini is thinking
- System instructions encouraging direct, helpful answers and honest uncertainty
- API errors, quota limits, and network failures handled with readable messages
- API key read from an environment variable; no key committed to Git
- Console interface remains available
- Offline fallback if no API key is configured
- Automated unit tests and GitHub Actions

## 1. Requirements
- Python 3.10+
- Tkinter (included with most standard Windows Python installations; if missing, modify/repair the Python installation to include Tcl/Tk)
- Internet connection for live AI mode
- A Gemini API key from Google AI Studio: https://aistudio.google.com/app/apikey
- No third-party Python packages are required by the application

## 2. Configure the API key on Windows
Keep your key private. Do not paste it into source code, GitHub commits, screenshots, or chat messages.

**Temporary setup (only for the current PowerShell window):**
```powershell
$env:GEMINI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
python gui.py
```
Replace the placeholder locally with your key. Do not commit the command or key.

**Persistent setup for your Windows user:**
1. Open Windows Search and find “Edit environment variables for your account”.
2. Add a user variable named `GEMINI_API_KEY` and set its value to your key.
3. Close and reopen the terminal, then start CampusBot.

Optional: set `GEMINI_MODEL` to a model available to your API key. For example, if Google AI Studio confirms that `gemini-3.5-flash-lite` is available to your account, set it using:
```cmd
setx GEMINI_MODEL "gemini-3.5-flash-lite"
```
Close and reopen Command Prompt after using `setx`. Model availability can change; use a model listed for your key in Google AI Studio.

## 3. Run
- **Desktop GUI:** double-click `run_gui.bat`, or run `python gui.py`.
- **Console:** double-click `run_chatbot.bat`, or run `python main.py`.
- **Tests:** run `python -m unittest -v` or double-click `run_tests.bat`.
- In the GUI, use Send or press Enter. Use Clear conversation to reset in-memory context; Show saved history to review local CSV turns. You can also type `help`, `clear`, `history`, or `exit` into the message field.

## 4. How it works
The GUI uses `gui.py`; the console remains in `main.py`. Both call `nlp_engine.py`, which sends the user's message and up to 12 recent user/model messages to Gemini. The GUI performs network work in a background thread so the window stays responsive. `storage.py` stores chat turns in a local CSV file. Saved CSV history is for review and is not automatically sent to the AI.

## 5. Security and limitations
- Your API key is sent to Google's Gemini API over HTTPS and must be protected.
- Do not commit your key to GitHub or share it in screenshots or chat.
- API availability, rate limits, model access, and pricing depend on your Google AI Studio account and current terms.
- Without a key, CampusBot is limited to simple built-in replies and cannot provide real generative answers.
- The chatbot may still be wrong; verify important information.
- Local CSV history is not encrypted. This is a student project, not an official college service.

## Project structure
- `gui.py` — Tkinter desktop GUI and asynchronous response handling
- `main.py` — console chat loop and commands
- `nlp_engine.py` — Gemini API integration and NLP helpers
- `storage.py` — local CSV persistence
- `test_chatbot.py` — automated tests
- `run_gui.bat` — Windows desktop GUI launcher
- `run_chatbot.bat` — Windows console launcher
- `PROJECT_REPORT.md` — report draft
- `PROJECT_OUTCOMES.md` — learning outcomes
- `TEST_RESULTS.md` — CI test results

## 6. Troubleshooting
- If the GUI says **Limited offline mode**, configure `GEMINI_API_KEY`, close the terminal, and reopen it.
- If Windows says Tkinter is unavailable, repair or reinstall Python with Tcl/Tk support enabled.
- For a 404 model error, set `GEMINI_MODEL` to a model available to your key.
- For a 429 error, check Google AI Studio quota.
- If the app misunderstands a question, clarify the request and correct the assumption. Verify important facts and code independently.
