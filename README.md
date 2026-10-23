# CampusBot — Single-File Python AI Chatbot

**Use `CampusBot.py` as the complete, standalone application.** It contains the Tkinter desktop GUI, optional console mode, Gemini API connection, lightweight NLP helpers, conversation context, and local CSV history in one Python file. You do not need to combine or copy code from separate modules to run this version.

## Features
- Desktop chat window with Send and Enter-to-send
- Gemini AI answers and follow-up conversation context
- Background requests to keep the GUI responsive
- Clear conversation and view locally saved chat history
- Console mode using the same code file
- CSV history saved beside the script
- Friendly handling of common API, quota, model, and network errors
- No third-party Python packages required

## Requirements
- Python 3.10 or newer
- Tkinter/Tcl-Tk installed for desktop mode
- Internet and a valid Gemini API key for live AI responses

## 1. Configure Gemini once on Windows
Create a key in Google AI Studio: https://aistudio.google.com/app/apikey

In PowerShell, set the key for the current terminal session (replace the placeholder locally):
```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
$env:GEMINI_MODEL = "gemini-3.5-flash-lite"
python CampusBot.py
```

The default model is `gemini-3.5-flash-lite`, based on the model used for this project. Model availability can change; if Google AI Studio shows it is unavailable for your key, set `GEMINI_MODEL` to a model available to your account. **Never paste your real key into the source file or commit it to GitHub.**

For future sessions, set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` in Windows **User environment variables**, then reopen the terminal.

## 2. Run the application
Open a terminal in the folder containing `CampusBot.py` and run:

- **Desktop GUI (recommended):** `python CampusBot.py`
- **Console:** `python CampusBot.py --console`

Without an API key, the application runs in limited offline mode with a few built-in replies; open-ended AI answers require Gemini. Chat turns are saved in `chat_history.csv` in the same folder. The saved history is for local review and is not automatically sent as context to Gemini.

## 3. Project report
Open [PROJECT_REPORT.md](PROJECT_REPORT.md) for the academic report draft. Fill in the student-specific fields and align it with the exact college submission template before submitting.

## 4. Security and limitations
- Keep your Gemini API key private; it is sent to Google's API over HTTPS.
- CSV chat history is stored locally and is not encrypted. Do not store passwords, API keys, or confidential information in chat.
- Gemini may make mistakes; verify important facts and code.
- CampusBot is a student project, not an official college service.

## Repository maintenance
`CampusBot.py` is the standalone file intended for simple running and submission. The older modular source files and automated tests remain in the repository for development history and regression testing; they are not required to run the standalone version.
