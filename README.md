# CampusBot — Python AI Chatbot

**Run `CampusBot.py` for the standalone desktop application.** It contains the Tkinter GUI, shared AI connection, recent conversation context, and local CSV history.

## Features
- Desktop chat window with Send and Enter-to-send
- Shared Gemini-powered backend; friends do not need their own API key
- Background network requests to keep the GUI responsive
- Conversation context for follow-up questions
- Clear conversation and view locally saved chat history
- CSV history saved beside the script
- Prompt instructions for handling typos, misspellings, missing words, informal grammar, and multi-part questions
- Concise answers by default while aiming to answer every part
- Friendly handling of network and backend errors
- Automated regression tests through GitHub Actions

## Requirements
- Python 3.10 or newer
- Tkinter/Tcl-Tk installed
- Internet connection for live AI responses

## Run CampusBot

Download `CampusBot.py` from this repository, or download the repository ZIP and extract it. Open a terminal in the folder containing the file and run:

```powershell
python CampusBot.py
```

The app connects to the shared backend at https://campusbot-ai-backend.onrender.com by default. **Friends do not need to create or enter a Gemini API key.** A Render free service may take longer to answer its first request after inactivity while it wakes up.

## Reply quality and speed

The shared backend uses Gemini Flash by default, a compact system prompt, a bounded recent conversation context, and a 1,024-token output limit to reduce avoidable generation work. The prompt asks the AI to interpret typos and missing words, use context for follow-ups, answer all parts, and be concise by default. These settings can help reduce unnecessary latency but cannot guarantee a response time; network conditions, Render wake-up, Gemini availability, and quota still matter.

The current client displays the response after the full reply has arrived; token-by-token streaming is not implemented yet. The app does not currently perform live web search, so users should verify changing facts against authoritative current sources.

## Optional developer configuration

`CAMPUSBOT_BACKEND_URL` can override the shared backend URL. Leave it at its default for normal use. The client does not accept a direct Gemini API key; the key is kept privately in the backend's Render environment settings.

Never paste a real API key into source code, chat, or GitHub.

## Chat history

Chat turns are saved in `chat_history.csv` in the same folder for local review. Conversation context is sent to the shared AI backend to support follow-up questions, but the CSV file itself is not uploaded. Do not enter passwords, API keys, or confidential information in chat; CSV history is stored locally and is not encrypted.

## Project report

Open [PROJECT_REPORT.md](PROJECT_REPORT.md) for the updated academic report. Fill in student-specific fields and align it with the exact college submission template before submitting.

## Tests

Run locally:

```powershell
python -m py_compile CampusBot.py server.py tests/test_campusbot.py
python -m unittest discover -s tests -v
```

GitHub Actions runs compilation and regression tests on pushes and pull requests to `main`. The tests mock network replies; they do not prove live Gemini availability or measure real response latency.

## Security and limitations

- Shared AI requests use HTTPS to the project's hosted backend, which calls Google's Gemini API.
- The backend is public and applies basic rate limiting; do not treat it as a private or production-grade service.
- AI may make mistakes; verify important facts and code.
- CampusBot is a student project, not an official college service.

## Repository maintenance

`CampusBot.py` is the standalone GUI file intended for simple running and submission. Older modular source files and tests remain for development history and regression testing; they are not required to run the standalone app.
