# Project Outcomes — CampusBot Conversational AI

## Aim
Develop a conversational Python chatbot with a desktop GUI and console option, using a live generative AI service when configured.

## Implemented features
- Tkinter desktop chat window with transcript, message entry, Send button, and Enter-to-send.
- Background Gemini calls to keep the GUI responsive.
- Live Gemini API integration using Python's standard-library HTTPS client.
- Recent-turn context for follow-up questions.
- Clear-context control and saved CSV history viewer.
- Console interface retained as an alternative.
- Helpful handling for missing API keys, invalid credentials, quota limits, network problems, and malformed responses.
- API key read from the GEMINI_API_KEY environment variable and not stored in source code.
- Offline fallback for simple commands when the API key is absent.
- Automated tests that mock the AI API, so tests do not consume API quota.

## Learning outcomes
After studying and demonstrating the project, a student should be able to:
1. Explain the difference between rule-based chatbot responses and generative AI.
2. Explain basic text preprocessing and intent detection.
3. Integrate a REST API using JSON over HTTPS.
4. Use environment variables to keep secrets out of source code.
5. Maintain short conversational context with user/model roles.
6. Explain why background threads and queues help keep a GUI responsive.
7. Build a desktop interface using Tkinter widgets and event handlers.
8. Store chat turns in CSV and test Python functions with unittest.
9. Explain AI limitations, privacy considerations, and the need to verify important information.

## Setup before demonstrating live AI
1. Obtain a Gemini API key through Google AI Studio: https://aistudio.google.com/app/apikey
2. Set the local environment variable GEMINI_API_KEY; follow README.md.
3. Double-click run_gui.bat to open the desktop GUI, or run python gui.py.
4. Ask a general question, then ask a follow-up referencing the previous answer.
5. Use Clear conversation to demonstrate resetting context.
6. Use Show saved history to demonstrate CSV persistence.
7. Run python -m unittest -v.

## Important evaluation note
The automated tests mock the network response and validate integration logic without using a real key. Live AI quality, availability, quota, and account access depend on the user's Gemini setup and must be demonstrated with a valid key.

## Limitations
- Live mode requires internet access, a valid API key, an enabled model, and available quota.
- AI responses may be wrong; verify important facts.
- Recent context is held in memory only during the current run.
- CSV chat history is local and not encrypted.
- This is a classroom prototype, not an official college service.

## Future scope
Streaming responses, configurable model selection, retrieval from verified documents, explicit citations, and packaging as a desktop executable.
