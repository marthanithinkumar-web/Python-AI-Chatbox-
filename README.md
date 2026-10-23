# CampusBot — AI Chatbot Using Python and NLP

A beginner-friendly, offline college-information chatbot for a Python laboratory. It demonstrates a small NLP pipeline without paid APIs or external packages.

## Features
- Case-insensitive tokenization, stop-word removal, and synonym normalization
- Keyword-overlap intent classification and predefined responses
- Courses, exams, attendance, fees, library, timetable, contact, help, greetings, thanks, and about
- Safe fallback for unmatched questions
- CSV conversation history and history viewing
- Input validation, recursive word-count helper, and automated tests
- GitHub Actions workflow to run tests automatically

## Requirements
Python 3.10 or later. No third-party packages, internet, or API key are required.

## Run on Windows
1. Install Python 3.10+ and select Add Python to PATH.
2. Download this repository as a ZIP and extract it.
3. Open PowerShell or Command Prompt in the extracted folder.
4. Run: **python main.py**
5. Run tests: **python -m unittest -v**

If python is unavailable, try **py main.py** and **py -m unittest -v**.

## Project files
- main.py — console application and conversation loop
- nlp_engine.py — tokenization, preprocessing, intent classification, response selection
- storage.py — CSV history
- test_chatbot.py — automated unit tests
- PROJECT_REPORT.md — editable report draft
- PROJECT_OUTCOMES.md — learning outcomes
- SAMPLE_OUTPUT.md — example transcript

## Scope and privacy
This is a classroom prototype, not an official college chatbot. It does not connect to a college database or provide verified live dates, fees, or personal records. It directs users to official sources for changing information. Do not enter passwords, payment information, or confidential data.
