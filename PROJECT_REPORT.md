# COURSE END PROJECT REPORT

## CampusBot — AI Chatbot Development Using Python and NLP

**Course:** Essentials of Python Programming Laboratory (A9514)  
**Academic year:** 2026–2027  
**Branch / year:** CSD, B.Tech II Year  
**Student name:** Martha Nithin Kumar  
**Roll number:** ____________________  
**Batch / section:** ____________________  
**Course instructor:** Mr. B. Nagulu, Assistant Professor, CSD  
**Institution:** Vardhaman College of Engineering

> Fill in the roll number, batch/section, submission date, and any fields required by the college before submitting.

## Certificate

This is to certify that the course end project entitled “CampusBot: AI Chatbot Development Using Python and NLP” has been carried out by Martha Nithin Kumar as part of the requirements for Essentials of Python Programming Laboratory (A9514) during the academic year 2026–2027.

Course Instructor: ____________________  
Head of the Department: ____________________  
Date: ____________________

## Declaration

I declare that this report describes the CampusBot project and its implementation to the best of my knowledge. External technical resources used for the implementation are acknowledged in the references.

Signature: ____________________  
Date: ____________________

## Acknowledgement

I express my sincere gratitude to Mr. B. Nagulu, course instructor, and the Department of Computer Science and Engineering (Data Science), Vardhaman College of Engineering, for the guidance and opportunity to undertake this project. I also thank my institution and everyone who supported the learning and testing of this application.

## Abstract

CampusBot is an AI-powered conversational chatbot built with a Python Flask backend and a hosted large language model accessed through the Groq API. It accepts natural-language questions and returns generated answers, with instructions designed to handle spelling mistakes, missing words, informal grammar, and follow-up questions. The backend validates incoming messages, includes bounded recent conversation history, limits repeated requests, and returns readable errors when the provider or network fails. The API credential is configured as a server-side environment variable on Render rather than embedded in source code. The deployed project was tested with greeting and general-question prompts, and the user confirmed that the chatbot was returning satisfactory replies after the latest fix. The system remains dependent on internet connectivity, provider availability, model access, and usage limits; generated answers should be checked when accuracy or current facts matter.

**Keywords:** Python, Natural Language Processing, Generative AI, Flask, Groq API, REST API, JSON, Render, chatbot.

## 1. Introduction

A chatbot is a software application that enables users to communicate with a computer system through natural language. Traditional rule-based chatbots rely on predefined keywords and responses and can fail when a user makes spelling errors or phrases a question unexpectedly. Generative AI models can produce more flexible responses based on the prompt and conversation context.

CampusBot connects a Python Flask backend to a hosted language model through the Groq chat-completions API. A client sends a question to the backend over HTTP, the backend forwards the message and a limited conversation history to the model, and the generated response is returned to the client as JSON. The backend is hosted on Render.

## 2. Problem Statement and Objectives

### 2.1 Problem Statement

Users often type short, informal or misspelled questions. A basic fixed-response chatbot may not understand these variations or follow-up questions. This project addresses the problem by integrating a generative AI model while keeping API credentials on the server and providing controlled error messages when a request cannot be completed.

### 2.2 Objectives

- Develop a conversational chatbot backend using Python and Flask.
- Connect the backend to a hosted generative AI model through the Groq API.
- Support natural-language questions and bounded recent conversation context.
- Validate requests and provide understandable errors for invalid input, rate limits and provider failures.
- Protect the API credential using a server-side environment variable.
- Deploy the backend to Render and verify live question-and-answer behaviour.

## 3. Requirements and Feasibility

### 3.1 Software Requirements

| Component | Technology / purpose |
|---|---|
| Programming language | Python 3 |
| Web framework | Flask |
| AI service | Groq Chat Completions API |
| Configured model | `openai/gpt-oss-120b` (Render environment setting at time of report) |
| Transport / format | HTTPS, HTTP POST, JSON |
| Hosting | Render |
| Source control | Git and GitHub |
| Configuration | `GROQ_API_KEY` and `GROQ_MODEL` environment variables |

### 3.2 Hardware Requirements

A standard computer capable of using a modern web browser and an internet connection is sufficient for testing the hosted application. Model inference runs through the hosted API rather than locally on the user's computer.

### 3.3 Feasibility

Technical feasibility is supported by Python, Flask, HTTP/JSON and a hosted API. Operational feasibility is supported by a simple chat interface and readable error responses. Economic feasibility depends on the provider's current quota and pricing terms, which may change and should be checked before sustained use.

## 4. System Architecture and Design

### 4.1 Architecture

```text
User / Chat Interface
        |
        | HTTPS POST with JSON message and recent history
        v
CampusBot Flask Backend (Render)
  - request validation
  - per-IP request limiting
  - prompt and context construction
  - server-side API key retrieval
        |
        | HTTPS request with Authorization header
        v
Groq Chat Completions API
        |
        | generated assistant message
        v
Flask backend returns JSON reply to client
```

### 4.2 Request Flow

1. The user enters a message in the chat interface.
2. The client sends a JSON POST request to the `/chat` endpoint.
3. The backend checks request frequency, API configuration, JSON structure and message content.
4. The backend builds a system instruction, includes bounded recent history and appends the new user message.
5. The backend sends the request to Groq using the configured model and server-side `GROQ_API_KEY`.
6. The backend parses the generated content and returns a JSON reply.
7. If the provider rejects the request or a network problem occurs, the backend logs safe diagnostics and returns a controlled error.

### 4.3 Main Backend Components

| Component | Responsibility |
|---|---|
| Flask application | Defines service and chat routes. |
| Request validation | Rejects empty, malformed or unsupported input. |
| Rate limiting | Limits repeated requests from an IP within a rolling time window. |
| Prompt/context builder | Adds the system instruction and bounded recent messages. |
| Groq API client logic | Sends the HTTP request, reads the response and extracts the answer. |
| Error handling | Handles HTTP errors, timeouts, connection errors and unreadable responses. |
| Environment configuration | Reads `GROQ_API_KEY` and `GROQ_MODEL` from environment variables. |

## 5. Implementation

### 5.1 Important Files and Settings

| File / setting | Purpose |
|---|---|
| `server.py` | Flask backend, validation, rate limiting, provider call and error handling. |
| `requirements.txt` | Lists Python packages required by the backend. |
| `GROQ_API_KEY` | Secret API key stored in Render environment variables; never include the value in source code or this report. |
| `GROQ_MODEL` | Model identifier configured in Render; currently reported as `openai/gpt-oss-120b`. |
| GitHub repository | Stores version-controlled project source. |
| Render service | Hosts the backend at https://campusbot-ai-backend.onrender.com. |

### 5.2 API Endpoint

The `POST /chat` endpoint accepts a JSON object containing a message and optional history. A successful response contains a `reply` field. Invalid input and provider failures return a JSON error message with an appropriate HTTP status.

Request example:

```json
{
  "message": "WHAT IS PYTHON?",
  "history": []
}
```

Successful response shape:

```json
{
  "reply": "Python is a high-level programming language ..."
}
```

### 5.3 Prompt and Context Handling

The system instruction asks the model to answer directly, understand common typing mistakes and follow-up questions, use examples when helpful, and avoid inventing changing facts. The backend accepts supported conversation roles and bounds the amount of recent history included in the request. This helps keep requests controlled but does not guarantee that every answer will be correct.

### 5.4 API Error Handling

The backend handles common failures such as missing configuration, invalid input, rate limiting, authentication errors, forbidden requests, unavailable models, and connection or timeout failures. Provider diagnostics are written to application logs without logging the Authorization header or API key. During troubleshooting, Groq requests returned HTTP 403 with error code 1010. The backend was updated to log provider response details safely and to send an explicit `User-Agent` header.

## 6. Testing and Results

### 6.1 Test Cases

| ID | Test | Expected behaviour | Result / evidence |
|---|---|---|---|
| TC01 | Send greeting: `HI` | A natural greeting reply is returned. | User-confirmed pass |
| TC02 | Ask a general question: `WHAT` | An understandable AI-generated response is returned. | User-confirmed pass |
| TC03 | Ask a question with spelling mistakes | Model attempts to infer intent and respond helpfully. | Test separately before claiming pass |
| TC04 | Submit an empty message | Backend rejects the request with a readable validation error. | Verify in local or hosted test |
| TC05 | Send malformed JSON | Backend returns a controlled client error. | Verify in local or hosted test |
| TC06 | Exceed configured request rate | Backend returns a rate-limit error. | Verify in local or hosted test |
| TC07 | Provider rejects a request | Backend logs safe diagnostics and returns a controlled error. | Observed during troubleshooting |
| TC08 | Inspect API-key handling | Key remains in Render environment configuration. | Configuration requirement |
| TC09 | Inspect backend health route | Health endpoint reports service status and key-configuration status. | Verify against current implementation |

### 6.2 Results and Discussion

During deployment troubleshooting, Groq requests initially returned HTTP 403 with error code 1010. The backend was updated to log provider response details safely and to send an explicit `User-Agent` header. The user subsequently confirmed that the chatbot's replies were satisfactory. This is a user-confirmed functional smoke test, not a formal benchmark of accuracy, latency or availability.

### 6.3 Screenshots to Add Before Submission

- Screenshot 1: CampusBot application open in a browser.
- Screenshot 2: A successful greeting response.
- Screenshot 3: A general question and the generated answer.
- Screenshot 4: Render service showing the live deployment (hide secrets).
- Screenshot 5: GitHub repository showing the final source files.

## 7. Security, Limitations and Future Scope

### 7.1 Security

- Keep `GROQ_API_KEY` only in Render environment variables or a suitable secret manager.
- Never commit API keys, private chat histories or credentials to GitHub.
- Use HTTPS for communication with the hosted backend and provider.
- Do not send passwords or sensitive personal information to the chatbot.
- Review logs to ensure diagnostic messages never contain authorization headers or secrets.

### 7.2 Limitations

- Responses require internet access and availability of the Render service and Groq API.
- Response quality depends on the selected model, prompt, context and provider service.
- The chatbot does not guarantee factual correctness and should not be treated as an official source.
- Live web search or verified college-document retrieval is not described as a current feature of this backend.
- Response times can vary; no controlled latency benchmark has been recorded.

### 7.3 Future Scope

- Add verified retrieval from college documents and show citations to source material.
- Measure request latency across repeated tests and report median and percentile timings.
- Add automated integration tests for the backend's request validation and response parsing.
- Consider response streaming to display partial output earlier.
- Improve monitoring for uptime, API quota and provider errors.

## 8. Conclusion

CampusBot demonstrates how a Python Flask backend can integrate a hosted generative AI model through a chat API. The project includes request validation, limited conversation context, rate limiting, environment-based secret management and controlled error handling. The deployed application was confirmed by the user to produce satisfactory replies after troubleshooting the provider request. The system is a student prototype: users should verify important information, and the service depends on network access and provider availability.

## References

1. Groq, “API Reference — Chat Completions.” https://console.groq.com/docs/api-reference
2. Groq, “Text Generation.” https://console.groq.com/docs/text-chat
3. Groq, “Security Onboarding.” https://console.groq.com/docs/production-readiness/security-onboarding
4. Python Software Foundation, “Python Documentation.” https://docs.python.org/3/
5. Pallets Projects, “Flask Documentation.” https://flask.palletsprojects.com/
6. GitHub, “GitHub Actions Documentation.” https://docs.github.com/actions
7. Render, “Render Documentation.” https://render.com/docs

## Appendix A — Run and Deployment Notes

The hosted backend base URL is https://campusbot-ai-backend.onrender.com. The `/health` endpoint reports backend health and whether the API key is configured, and `/chat` handles chat POST requests. For local execution, install packages listed in `requirements.txt`, set `GROQ_API_KEY` as an environment variable, set `GROQ_MODEL` if needed, and start the Flask application using the repository's documented command. Do not place the real API key in the report or commit it to source control.

## Appendix B — Viva Questions

1. What is a chatbot, and how does generative AI differ from a rule-based chatbot?
2. What is Flask and why is it used in this project?
3. What is a REST API?
4. Why are HTTP and JSON used for client-server communication?
5. What is the role of the Groq API?
6. Why is `GROQ_API_KEY` stored as an environment variable?
7. What is conversation history and why is it bounded?
8. What is rate limiting?
9. How are provider and network errors handled?
10. Why can an AI answer be incorrect even when the request succeeds?
11. What is the purpose of deployment on Render?
12. What improvements could be added in a future version?
