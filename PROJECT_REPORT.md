# PROJECT REPORT

## CampusBot — AI Chatbot Using Python and Generative AI

**Project title:** CampusBot — AI Chatbot Using Python and Generative AI  
**Course:** Essentials of Python Programming Laboratory  
**Academic year:** 2026–2027  
**Branch / year:** CSD, B.Tech II Year  
**Student name:** ____________________  
**Roll number:** ____________________  
**Batch / section:** ____________________  
**Course instructor:** Mr. B. Nagulu, Assistant Professor, CSD  
**Institution:** Vardhaman College of Engineering

> Fill in student-specific fields and match any required college cover page, certificate, and formatting template before submission.

## Certificate

This is to certify that the project titled “CampusBot — AI Chatbot Using Python and Generative AI” is submitted as part of the Essentials of Python Programming Laboratory course requirements for the academic year 2026–2027 by the student named above.

Instructor signature: ____________________  Date: __________

## Declaration

I declare that this report describes the CampusBot desktop chatbot project and its current implementation. External technical references are listed at the end of the report.

Signature: ____________________  Date: __________

## Acknowledgement

I thank the course instructor and department for the opportunity to apply Python programming concepts through this project.

## Abstract

CampusBot is a Python desktop chatbot with a Tkinter graphical interface and a shared, hosted Gemini AI backend. The desktop client is designed to be easy to run: users do not need to place a Gemini API key in the desktop application. The GUI supports typing or pressing Enter to send a message, viewing the conversation, clearing the current conversation context, and opening locally saved CSV chat history. Network requests run in a background thread so the window can remain responsive while the backend generates a reply. The backend keeps the Gemini credential in the Render service environment, sends recent conversation context to Gemini, validates incoming requests, limits request frequency, and returns readable errors for provider or network failures. The prompt is designed to understand typos, missing words, imperfect grammar, and follow-up questions; answer all parts of a request; and avoid confidently inventing changing facts. The project includes automated regression tests and a GitHub Actions workflow. AI answers still require verification, and live response speed depends on network conditions, service wake-up time, Gemini latency, and provider quota.

## 1. Introduction

A chatbot provides a conversational way for a user to ask questions and receive responses. CampusBot combines a Python desktop GUI with a generative AI service to support flexible, natural-language questions rather than relying only on fixed keyword responses. Tkinter provides the desktop interface, Python's standard library handles HTTP requests and local CSV history, and a Flask backend securely calls Gemini.

## 2. Problem statement

A basic rule-based chatbot often struggles with spelling mistakes, missing words, informal phrasing, and follow-up questions. CampusBot aims to accept natural language more flexibly while keeping the interface responsive during network activity. It should preserve useful recent context, return understandable errors when the service is unavailable, and avoid presenting uncertain or changing information as guaranteed fact.

## 3. Objectives

- Build a straightforward Python desktop chatbot with a Tkinter GUI.
- Use a shared Gemini-powered backend so users do not need their own API key.
- Improve understanding of typos, misspellings, missing words, informal phrasing, and follow-up questions.
- Keep the desktop interface responsive while the network request runs.
- Keep answers direct and reasonably concise by default while answering every part of a question.
- Preserve recent conversational context for follow-up questions.
- Save completed exchanges in a local CSV file and provide a history viewer.
- Handle network, malformed-response, HTTP, quota, and configuration errors gracefully.
- Keep the Gemini API key on the backend rather than in the desktop source or repository.
- Run automated regression checks through GitHub Actions.

## 4. Software and hardware requirements

**Software:** Python 3.10 or newer, Tkinter/Tcl-Tk, an internet connection, GitHub repository, and a hosted backend.  
**Desktop dependencies:** Python standard library; no third-party package is required for the desktop client.  
**Backend dependencies:** Flask and Gunicorn, as listed in `requirements.txt`.  
**AI service:** Google Gemini API access configured on the backend.  
**Hardware:** A computer capable of running Python and Tkinter.

## 5. System architecture

1. The user types a question in the CampusBot window and presses Send or Enter.
2. The client validates that the message is not blank and that another request is not already running.
3. The client sends the message and recent conversation context to the hosted backend over HTTPS in a background thread.
4. The Flask backend validates the request, applies basic rate limiting, and reads `GEMINI_API_KEY` from the server environment.
5. The backend submits the conversation to the configured Gemini model and parses the generated answer.
6. The desktop client receives the result through a thread-safe queue and updates the GUI.
7. The completed exchange is appended to `chat_history.csv` in the local application folder.

```text
User
  ↓
Tkinter desktop GUI
  ↓ HTTPS request + recent context (background thread)
CampusBot Flask backend on Render
  ↓ Gemini API request (server-side secret)
Google Gemini
  ↓ generated reply
Backend → desktop queue → chat transcript
                         ↓
                  local CSV history
```

## 6. Main modules and files

- **`CampusBot.py`:** The standalone desktop application. It includes the Tkinter GUI, backend HTTP client, recent-context management, background requests, error handling, CSV history, and application entry point.
- **`server.py`:** Flask API hosted separately. It validates chat requests, applies basic per-IP request limiting, sends prompts to Gemini, and returns the reply or a controlled error.
- **`requirements.txt`:** Backend Python dependencies.
- **`.env.example`:** Example configuration names; it must not contain real secrets.
- **`tests/test_campusbot.py`:** Regression tests for client behavior using mocked network responses.
- **`.github/workflows/campusbot-tests.yml`:** Runs Python compilation and regression tests on pushes and pull requests.
- **`chat_history.csv`:** Runtime data created beside the desktop script when conversations are saved. It is not source code and should not be committed with private conversation content.
- **`README.md`:** Setup and run instructions.

## 7. Natural-language understanding and response quality

CampusBot uses a generative AI model rather than training a language model itself. Its backend instructions ask Gemini to:
- interpret spelling mistakes, missing words, imperfect grammar, and follow-up questions using context;
- address all meaningful parts of a multi-part question;
- start with the answer rather than lengthy filler;
- provide examples when they improve understanding;
- ask for clarification only when ambiguity materially affects the answer;
- acknowledge uncertainty and avoid inventing facts, citations, dates, fees, college policies, or live status.

These are instructions to the model, not a guarantee that every answer will be correct. The application has no dedicated web-search/retrieval pipeline in the current implementation, so changing facts should be checked against authoritative current sources rather than assumed to have been live-verified by CampusBot.

## 8. Response-speed measures and limitations

The client makes the HTTP request on a background thread so the GUI does not freeze during generation. The backend uses Gemini Flash by default and keeps the prompt compact. The backend is configured to limit generated output to 1,024 tokens, which helps avoid unnecessarily long generations while leaving room for useful answers. It passes only recent conversation context rather than an unlimited transcript. Answers are expected to be concise by default, but the model should still answer all parts of a question.

These changes reduce avoidable prompt/output work; they do not guarantee a fixed response time. Actual latency depends on the Render service waking from inactivity, the user's internet connection, Gemini response time, model availability, and quota. The current client receives the complete reply before showing it; **token-by-token streaming is not implemented**. Streaming remains a possible next improvement to show the first words earlier, although it would not necessarily reduce total generation time. No numeric speed improvement is claimed because no controlled latency benchmark has been recorded.

## 9. Conversation context, history, and privacy

The client keeps recent conversation turns in memory during the active session and sends a bounded context window for follow-up questions. The Clear conversation control removes the active in-memory context; it does not erase saved CSV history. Show saved history reads the most recent saved exchanges from the local file. The CSV is stored locally and is not encrypted. The backend receives the current question and recent context to generate a response. Users should not enter passwords, API keys, or sensitive personal information.

The Gemini API key must remain in the Render environment variable `GEMINI_API_KEY`; it must never be embedded in the desktop application, checked into GitHub, or included in the report.

## 10. Test plan

Run the automated suite from the repository root:

```powershell
python -m py_compile CampusBot.py tests/test_campusbot.py
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs these checks automatically for pushes and pull requests to `main`. The test suite uses mocked HTTP responses and checks:
- successful reply parsing and recent-context payload;
- empty reply handling;
- HTTP/rate-limit error handling;
- network failure handling;
- malformed JSON handling;
- missing backend URL handling;
- bounded conversation history;
- CSV history read/write round-trip.

Passing mocked tests validates the tested application logic; it does not prove that a real Gemini request will succeed or measure live latency. A separate desktop smoke test should launch the GUI, send a normal question, ask a follow-up, try a typo-filled question, clear the conversation, and inspect saved history.

## 11. Results and discussion

The current project is a GUI-only desktop client connected to a shared backend, rather than the earlier console-plus-GUI design described in some legacy files. The client is intended to run with `python CampusBot.py`; friends do not need a Gemini API key. Background requests and a queue separate network work from Tkinter UI updates. The backend keeps the API key off the client and returns user-readable errors for several common failure cases. Regression tests run in GitHub Actions.

The quality of a reply depends on the prompt, the recent context, Gemini's output, and the current availability of the hosted service. The program is not a source of official college policy. Current deadlines, fees, schedules, and other changing information must be confirmed from authoritative sources.

## 12. Conclusion

CampusBot demonstrates a practical Python desktop GUI, HTTP/JSON communication, a Flask API, integration with a hosted generative AI model, environment-based secret management, thread-safe UI updates, CSV file handling, exception handling, and automated tests. Its design aims to make natural-language interaction more flexible and keep the desktop interface responsive. The project remains a student prototype: live AI requires internet access, the hosted service, model access, and available quota, and AI-generated answers may be wrong.

## 13. Future scope

- Implement end-to-end Gemini streaming and show partial text as it arrives.
- Record request duration and first-token/complete-response timings to compare performance objectively.
- Add integration tests for the backend's request validation and response parsing.
- Add verified document retrieval and explicit citations for current or institution-specific information.
- Add cancellation and retry behavior that does not duplicate or corrupt history.
- Package the desktop client for simpler installation on Windows.

## 14. References

1. Python Software Foundation, Python documentation: https://docs.python.org/3/
2. Python Software Foundation, Tkinter documentation: https://docs.python.org/3/library/tkinter.html
3. Python Software Foundation, CSV documentation: https://docs.python.org/3/library/csv.html
4. Python Software Foundation, unittest documentation: https://docs.python.org/3/library/unittest.html
5. Flask documentation: https://flask.palletsprojects.com/
6. Google Gemini API documentation: https://ai.google.dev/gemini-api/docs
7. GitHub Actions documentation: https://docs.github.com/actions

## Viva questions

1. What is a chatbot?
2. What is the difference between rule-based responses and generative AI?
3. What is a REST API?
4. Why are JSON and HTTPS used?
5. Why should an API key be kept on the backend?
6. Why does the GUI use a background thread?
7. What is the purpose of a thread-safe queue?
8. How does conversation context help with follow-up questions?
9. Why is CSV used for local history?
10. What is the purpose of unit testing?
11. Why do mocked tests not prove live Gemini availability?
12. Why should changing facts be verified from official sources?

## Appendix A — Run instructions

1. Install Python 3.10 or newer with Tcl/Tk support.
2. Download or clone the repository and open a terminal in its folder.
3. Run:

```powershell
python CampusBot.py
```

4. Ask a question, then ask a follow-up that refers to the previous response.
5. Use **Clear conversation** to reset the current context and **Show saved history** to view saved exchanges.

The desktop client uses the shared backend at `https://campusbot-ai-backend.onrender.com` by default. Do not place a Gemini API key in the desktop source.

## Appendix B — Submission checklist

- [ ] Fill in student name, roll number, batch/section, and submission date if required.
- [ ] Match the report to the college's prescribed template.
- [ ] Run the regression tests and record the actual result.
- [ ] Launch the GUI on the target computer.
- [ ] Test a normal question, a typo-filled question, a follow-up, and a multi-part question.
- [ ] Demonstrate Clear conversation and Show saved history.
- [ ] Explain that streaming and live web search are not current features.
- [ ] Do not claim a measured speed improvement unless an actual benchmark has been run.
