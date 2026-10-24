# CampusBot — Single-File Python AI Chatbot

**Use `CampusBot.py` as the complete, standalone application.** It contains the Tkinter desktop GUI, optional console mode, AI connection, lightweight NLP helpers, conversation context, and local CSV history in one Python file.

## Features
- Desktop chat window with Send and Enter-to-send
- Shared Gemini-powered AI backend by default, so friends do not need their own API key
- Background requests to keep the GUI responsive
- Clear conversation and view locally saved chat history
- Console mode using the same code file
- CSV history saved beside the script
- Friendly handling of common API, quota, model, and network errors
- No third-party Python packages required for the desktop client

## Requirements
- Python 3.10 or newer
- Tkinter/Tcl-Tk installed for desktop mode
- Internet connection for live AI responses

## 1. Run CampusBot (recommended)

Download `CampusBot.py` from this repository, or download the repository ZIP and extract it. Open a terminal in the folder containing the file and run:

- **Desktop GUI (recommended):** `python CampusBot.py`
- **Console:** `python CampusBot.py --console`

The app connects to the shared backend at https://campusbot-ai-backend.onrender.com by default. **Friends do not need to create or enter a Gemini API key.** Because the backend is hosted on Render's free plan, its first request after inactivity may take a little longer while the service wakes up.

## 2. Optional developer configuration

The desktop client supports these environment variables:

- `CAMPUSBOT_BACKEND_URL`: override the shared backend URL. Set it to an empty string only if you intentionally want to use direct-key mode.
- `GEMINI_API_KEY`: required only for direct-key mode; keep it private.
- `GEMINI_MODEL`: optional model override for direct-key mode.

For direct-key mode, create a key in Google AI Studio at https://aistudio.google.com/app/apikey, then configure it locally. In PowerShell:

```powershell
$env:CAMPUSBOT_BACKEND_URL = ""
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
python CampusBot.py
```

Never paste a real API key into source code, chat, or GitHub. The shared backend's key is configured privately in Render's environment settings.

## 3. Chat history

Chat turns are saved in `chat_history.csv` in the same folder for local review. The saved history is not automatically uploaded as a full history file. Do not enter passwords, API keys, or confidential information in chat; CSV history is stored locally and is not encrypted.

## 4. Project report

Open [PROJECT_REPORT.md](PROJECT_REPORT.md) for the academic report draft. Fill in student-specific fields and align it with the exact college submission template before submitting.

## 5. Security and limitations
- Shared AI requests are sent over HTTPS to the project's hosted backend, which calls Google's Gemini API.
- The backend is public and applies basic rate limiting; do not treat it as a private or production-grade service.
- AI may make mistakes; verify important facts and code.
- CampusBot is a student project, not an official college service.

## Repository maintenance
`CampusBot.py` is the standalone file intended for simple running and submission. Older modular source files and automated tests remain in the repository for development history and regression testing; they are not required to run the standalone version.
