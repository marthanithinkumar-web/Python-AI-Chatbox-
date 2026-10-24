# CampusBot — Python AI Chatbot

**Desktop entry point: `CampusBot.py`.** This standalone Tkinter application connects to the hosted CampusBot backend, keeps recent conversation context in memory, and saves chat history to a local CSV file.

## Features

- Desktop chat window with Send and Enter-to-send
- Shared Groq-powered AI backend; users do not need their own API key
- Background network requests to keep the GUI responsive
- Recent conversation context for follow-up questions
- Clear conversation and view locally saved chat history
- Friendly handling of network and backend errors
- Automated regression tests through GitHub Actions

## Run the desktop application

Requirements: Python 3.10 or newer, Tkinter/Tcl-Tk, and an internet connection.

Open a terminal in this folder and run:

```powershell
python CampusBot.py
```

Or double-click `run_gui.bat` on Windows. The app uses `https://campusbot-ai-backend.onrender.com` by default. To use another compatible backend, set `CAMPUSBOT_BACKEND_URL` before starting the app.

A Render free service may take longer to answer the first request after inactivity while it wakes up. CampusBot waits for the complete reply; token-by-token streaming is not implemented. It does not perform live web search, so verify changing facts against authoritative current sources.

## Backend deployment

The Flask backend is in `server.py`; the deployment uses `requirements.txt` and should start with:

```bash
gunicorn server:app
```

Configure `GROQ_API_KEY` in the hosting provider's private environment settings. `GROQ_MODEL` is optional and selects the model. Never put a real API key in source code, chat, or GitHub.

The backend includes basic per-IP rate limiting and input-size limits. It is a student project, not a private or production-grade service. AI may make mistakes; verify important facts and code.

## Chat history and privacy

Completed exchanges are saved to `chat_history.csv` beside `CampusBot.py`. The CSV is local and is not uploaded by the client, but it is not encrypted. Recent conversation context is sent to the hosted AI backend to support follow-up questions. Do not enter passwords, API keys, or confidential information.

## Tests

Run the desktop-client regression tests locally:

```powershell
python -m py_compile CampusBot.py server.py tests/test_campusbot.py
python -m unittest discover -s tests -v
```

GitHub Actions compiles the desktop client and backend, then runs mocked client tests. These tests do not prove live Groq availability or measure production response latency.

## Project report

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for the academic report. Fill in student-specific fields and align it with the exact college submission template before submitting.
