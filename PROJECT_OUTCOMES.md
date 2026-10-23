# Project Outcomes — CampusBot Conversational AI

## Aim
Develop a conversational Python chatbot that uses a live generative AI service when configured and demonstrates NLP, API integration, context management, file handling, and testing.

## Implemented features
- Live Gemini API integration using Python's standard-library HTTPS client.
- General-purpose answers rather than a small fixed set of college-only responses.
- Recent-turn conversation context to support follow-up questions.
- A system instruction that encourages direct, clear answers and honest uncertainty.
- Helpful handling for missing API keys, invalid credentials, quota limits, network problems, and malformed responses.
- Local CSV history, clear-context command, help/history/exit commands.
- API key read from the GEMINI_API_KEY environment variable and not stored in source code.
- Offline fallback for simple commands when the API key is absent.
- Automated tests that mock the AI API, so tests do not consume API quota.

## Learning outcomes
After studying and demonstrating the project, a student should be able to:
1. Explain the difference between rule-based chatbot responses and generative AI.
2. Explain text preprocessing and simple intent detection.
3. Integrate a REST API using JSON over HTTPS.
4. Use environment variables to keep secrets out of source code.
5. Maintain short conversational context with user/model roles.
6. Handle HTTP errors, timeouts, quotas, and invalid responses.
7. Store chat turns in CSV and test Python functions with unittest.
8. Explain AI limitations, privacy considerations, and the need to verify important information.

## Setup before demonstrating live AI
1. Obtain a Gemini API key through Google AI Studio: https://aistudio.google.com/app/apikey
2. Set the local environment variable GEMINI_API_KEY; follow README.md.
3. Start with python main.py.
4. Ask a general question, then ask a follow-up referencing the previous answer.
5. Type clear and ask a new question to demonstrate context reset.
6. Run python -m unittest -v.

## Important evaluation note
The test suite mocks the network response and validates the integration logic without using a real key. Live AI quality, availability, quota, and account access depend on the user's Gemini setup and must be demonstrated with a valid key.

## Limitations
- Live mode requires internet access, a valid API key, an enabled model, and available quota.
- AI responses may be wrong; verify important facts.
- Recent context is held in memory only during the current run.
- CSV chat history is local and not encrypted.
- The application is a classroom prototype, not an official college service.

## Future scope
A graphical chat interface, streaming responses, configurable model selection, retrieval from verified documents, and explicit citations could be added in later versions.
