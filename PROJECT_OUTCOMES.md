# Project Outcomes — CampusBot Conversational AI

## Aim
Build a Python desktop chatbot with a Tkinter GUI, a shared Gemini-powered backend, recent conversation context, and local chat history.

## Implemented features
- Tkinter desktop chat window with transcript, message entry, Send, and Enter-to-send.
- Shared Gemini backend hosted separately from the desktop client; users do not need their own API key.
- Background HTTP request thread and thread-safe queue to keep the GUI responsive.
- Recent conversation context for follow-up questions.
- Prompt instructions to handle typos, misspellings, missing words, informal grammar, and multi-part questions.
- Direct, reasonably concise answers by default, while aiming to cover all parts of the question.
- Clear conversation control and locally saved CSV history viewer.
- Graceful handling of missing backend URL, HTTP errors, network problems, empty replies, and malformed responses.
- Server-side `GEMINI_API_KEY` configuration; no secret embedded in desktop source.
- Flask request validation, basic rate limiting, and controlled provider-error responses.
- Automated regression tests and GitHub Actions checks.

## Learning outcomes
A student should be able to:
1. Explain rule-based chatbots and generative AI.
2. Explain how a Python program sends JSON over HTTPS to a REST-style API.
3. Explain why API keys should remain server-side.
4. Use background threads and queues to keep a Tkinter interface responsive.
5. Pass bounded recent context to support follow-up questions.
6. Save and read local conversation data with CSV.
7. Test HTTP-client behavior with mocked responses and unittest.
8. Explain why model output and changing facts require verification.

## Setup and demonstration
1. Run `python CampusBot.py` on a computer with Python 3.10+ and Tkinter.
2. Ask a general question and then ask a follow-up that refers to it.
3. Test a question with misspellings or missing words.
4. Ask a multi-part question and check that the answer covers each part.
5. Use Clear conversation and Show saved history.
6. Run `python -m py_compile CampusBot.py tests/test_campusbot.py`.
7. Run `python -m unittest discover -s tests -v`.

## Limitations
- Live responses require internet, an available hosted backend, Gemini model access, and quota.
- Render free-service wake-up may add delay after inactivity.
- AI can be wrong and does not automatically verify live/current information.
- The current client waits for the full reply; token-by-token streaming is not implemented.
- No controlled latency benchmark has been recorded.
- CSV history is local and unencrypted.
- CampusBot is a student project, not an official college service.

## Future scope
Implement Gemini streaming, measure time-to-first-token and total response time, add backend integration tests, and retrieve/cite verified sources for current information.
