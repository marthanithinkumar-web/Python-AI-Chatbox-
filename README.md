# CampusBot — Single-File Python AI Chatbot

**Use `CampusBot.py` as the complete, standalone desktop application.** It contains the Tkinter GUI, shared AI connection, conversation context, and local CSV history in one Python file.

## Features
- Desktop chat window with Send and Enter-to-send
- Shared Gemini-powered AI backend; friends do not need their own API key
- Background requests to keep the GUI responsive
- Clear conversation and view locally saved chat history
- CSV history saved beside the script
- Friendly handling of network and backend errors
- No third-party Python packages required for the desktop client

## Requirements
- Python 3.10 or newer
- Tkinter/Tcl-Tk installed
- Internet connection for live AI responses

## Run CampusBot

Download `CampusBot.py` from this repository, or download the repository ZIP and extract it. Open a terminal in the folder containing the file and run:

```powershell
python CampusBot.py
```

The app connects to the shared backend at https://campusbot-ai-backend.onrender.com by default. **Friends do not need to create or enter a Gemini API key.** Because the backend is hosted on Render's free plan, its first request after inactivity may take a little longer while the service wakes up.

## Optional developer configuration

`CAMPUSBOT_BACKEND_URL` can override the shared backend URL. Leave it at its default for normal use. The client no longer supports direct Gemini-key mode; the Gemini key is kept privately in the backend's Render environment settings.

Never paste a real API key into source code, chat, or GitHub.

## Chat history

Chat turns are saved in `chat_history.csv` in the same folder for local review. Conversation context is sent to the shared AI backend to support follow-up questions, but the CSV file itself is not uploaded. Do not enter passwords, API keys, or confidential information in chat; CSV history is stored locally and is not encrypted.

## Project report

Open [PROJECT_REPORT.md](PROJECT_REPORT.md) for the academic report draft. Fill in student-specific fields and align it with the exact college submission template before submitting.

## Security and limitations
- Shared AI requests are sent over HTTPS to the project's hosted backend, which calls Google's Gemini API.
- The backend is public and applies basic rate limiting; do not treat it as a private or production-grade service.
- AI may make mistakes; verify important facts and code.
- CampusBot is a student project, not an official college service.

## Repository maintenance

`CampusBot.py` is the standalone GUI file intended for simple running and submission. Older modular source files and automated tests remain in the repository for development history and regression testing; they are not required to run the standalone version.
