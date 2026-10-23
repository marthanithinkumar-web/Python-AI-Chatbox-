# PROJECT REPORT
## AI Chatbot Development Using Python and Natural Language Processing

**Project title:** CampusBot — AI Chatbot Using Python and NLP  
**Course:** Essentials of Python Programming Laboratory  
**Academic year:** 2026–2027  
**Branch / year:** CSD, B.Tech II Year  
**Student name:** ____________________  
**Roll number:** ____________________  
**Batch / section:** ____________________  
**Course instructor:** Mr. B. Nagulu, Assistant Professor, CSD  
**Institution:** Vardhaman College of Engineering

> Complete student-specific fields and adapt this report to the exact college template before submission.

## Certificate
This is to certify that the project titled “AI Chatbot Development Using Python and Natural Language Processing” is submitted as part of the Essentials of Python Programming Laboratory course requirements for the academic year 2026–2027 by the student named above.

Instructor signature: ____________________  Date: __________

## Declaration
I declare that this report describes the CampusBot Python application developed for academic learning. External resources are listed in the references.

Signature: ____________________  Date: __________

## Acknowledgement
I thank the course instructor and department for guidance and the opportunity to practise Python programming through this project.

## Abstract
CampusBot is a standalone Python conversational chatbot contained in one runnable source file, CampusBot.py, with both a Tkinter desktop graphical user interface and a console interface. When a Gemini API key is configured, it sends the user's message and recent conversation turns to a generative AI model over HTTPS and displays the generated answer. The desktop GUI provides a chat transcript, message entry, Send button, clear-context control, saved-history viewer, and background API calls so the window remains responsive. The project also demonstrates basic NLP preprocessing, local CSV history, environment-variable-based secret management, API error handling, and automated tests that mock API responses. It requires Python 3.10 or later. Live mode requires internet access, a valid API key, model availability, and quota. It is a classroom prototype, not an official source of college information. The current GUI displays the answer after the complete API response has arrived; it does not yet stream partial text.

## 1. Introduction
Chatbots interact with people through conversational input. NLP concerns computational processing of human language. CampusBot's live mode uses a generative AI service. A Tkinter desktop interface makes the conversation easier to use than a terminal-only interaction, while the console version remains available for command-line demonstrations.

## 2. Problem statement
A small chatbot demonstrates how a Python application can accept natural-language messages, send them to a generative AI service, and display responses. The interface should remain usable during network requests and support follow-up questions. Because academic information changes, CampusBot avoids inventing dates, fees, or policies and directs users to official college sources.

## 3. Objectives
- Build an interactive Python chatbot with a desktop GUI and console option.
- Integrate Gemini for open-ended responses and follow-up context.
- Demonstrate tokenization, stop-word removal, and intent classification helpers.
- Save conversation history using CSV.
- Keep the GUI responsive while waiting for network responses.
- Validate behavior using automated tests and document limitations.

## 4. Tools and requirements
**Software:** Python 3.10+, Tkinter, text editor or IDE, GitHub.  
**Libraries:** tkinter, threading, queue, json, os, re, urllib, csv, pathlib, datetime, unittest.  
**Hardware:** Computer capable of running Python.  
**Connectivity:** Required for live Gemini mode; limited offline commands work without a key.

## 5. System design
1. User enters a message in the GUI or console.
2. The application checks for commands such as help, clear, history, and exit.
3. A normal message and recent conversation context are passed to the Gemini response engine.
4. In GUI mode, the API request runs in a background thread and the result is returned to the interface queue.
5. The response is displayed and the turn is saved to CSV.
6. The conversation continues until the user exits or closes the GUI.

~~~text
User → Tkinter GUI / Console → Gemini response engine → AI response
                   ↑                    ↓
                   └── UI queue     CSV history storage
~~~

## 6. Single-file implementation
- **CampusBot.py:** The complete runnable application. It contains the Tkinter GUI, console mode, lightweight NLP helpers, Gemini request/response handling, API error handling, conversation-context management, CSV history read/write, and the application entry point.
- **chat_history.csv:** Created automatically beside CampusBot.py when chat turns are saved; it is runtime data, not source code.
- The repository also retains earlier modular files and automated tests for development history and regression testing. They are not required to run CampusBot.py.

## 7. NLP and generative AI
**Tokenization:** Regular expressions extract lowercase alphanumeric tokens.  
**Stop-word removal:** Common grammatical words are removed for the lab demonstration.  
**Intent classification:** Basic keyword checks identify simple intents.  
**Generative response:** For open-ended questions, the application sends the message and recent context to Gemini with system instructions for clear answers, full coverage of multi-part questions, and honest uncertainty. The application does not train its own language model.

## 8. Python concepts
Variables, strings, lists, dictionaries, loops, conditionals, functions, modules, exception handling, regular expressions, file handling, CSV, JSON, HTTPS requests, environment variables, threads, queues, Tkinter widgets, and unit testing.

## 9. Test plan and cases
Run **python -m unittest -v**.

| Test | Expected behavior |
|---|---|
| Tokenization and preprocessing | Normalized tokens returned |
| Unknown intent | No false fixed intent claimed |
| Mocked Gemini response | Response parsed correctly without using API quota |
| API quota/model errors | Clear error messages returned |
| Blank input | User prompted again in console |
| Word count | Correct count returned |
| CSV round-trip | Stored message can be read back |
| GUI response integration | History is passed to response engine and updated turn is persisted |
| Context limit | Only recent conversation turns are retained |

Automated tests verify application logic using mocked API responses; they do not prove live Gemini availability. Repeat the tests locally and make a real Gemini request with a valid key before the demonstration.

## 10. Results and discussion
CampusBot.py provides a desktop GUI and a console interface backed by the same `generate_response()` function in a single source file. The GUI runs that function in a background thread and transfers completed results through a thread-safe queue, which helps prevent the Tkinter window from freezing during network calls. Conversation context is held in memory during a session, and each answered turn is saved to local CSV history. Generative AI can still make mistakes, so important facts and code should be checked.

### 10.1 GUI response timing and observed limitation
The GUI and console use the same non-streaming Gemini request function. The console prints the answer when the function returns; the GUI similarly waits for the complete answer before inserting it into the chat transcript. The GUI polls its result queue every 100 milliseconds, which normally contributes at most approximately one polling interval after a result is ready. This small polling interval alone does not explain a very large delay. If the GUI is consistently much slower than console mode for the same prompt, compare whether both sessions use the same `GEMINI_API_KEY`, `GEMINI_MODEL`, conversation context, and network conditions, and measure the API call duration before concluding that the GUI is the cause. The supplied implementation does not include measured benchmark results, so no numeric speed improvement is claimed.

### 10.2 Streaming is future work, not a current feature
The current endpoint is `generateContent`, which returns a complete response in this implementation. Streaming would require changing the request to Gemini's streaming endpoint and updating the GUI queue protocol to send text chunks and a completion/error event. The existing `poll()` handler currently expects one completed reply per queue item, so simply changing the endpoint without adapting the queue and display logic would not be a complete implementation. Streaming can improve perceived responsiveness by showing text as it arrives, but it does not guarantee a shorter total generation time.

## 11. Conclusion
CampusBot.py combines a Tkinter interface, console interface, live generative AI API, conversational context, NLP helpers, CSV persistence, secret handling, and API error management in one runnable source file. The repository's separate tests remain available for regression testing. It requires a valid Gemini API key and internet access for flexible answers. It is not an authoritative source for changing college policies or personal records.

## 12. Future scope
- Implement and test Gemini streaming in the GUI, displaying partial text as chunks arrive.
- Add timing diagnostics for request start, first response chunk, and full completion to distinguish API latency from GUI display latency.
- Ensure streaming errors and cancellation are handled cleanly without corrupting conversation history.
- Add configurable model selection in the UI.
- Add retrieval from verified documents and explicit citations where appropriate.
- Package the application as a desktop executable.

## 13. References
1. Python Software Foundation, Python 3 Documentation: https://docs.python.org/3/
2. Python Software Foundation, Tkinter documentation: https://docs.python.org/3/library/tkinter.html
3. Python Software Foundation, CSV File Reading and Writing: https://docs.python.org/3/library/csv.html
4. Python Software Foundation, unittest framework: https://docs.python.org/3/library/unittest.html
5. Google Gemini API documentation: https://ai.google.dev/gemini-api/docs

## Viva questions
1. What is a chatbot?
2. What is NLP?
3. Explain tokenization.
4. What is a generative AI API?
5. Why use environment variables for API keys?
6. Why use a background thread for network requests?
7. What does a queue do in the GUI?
8. Why use CSV history?
9. What is unit testing?
10. What are the limitations of generative AI?
11. How does the clear-context feature work?
12. Why should a chatbot not invent exam dates?


## Appendix A — Reproducible run commands

Run the desktop interface from the folder containing `CampusBot.py`:

```powershell
python CampusBot.py
```

Run the console interface from the same folder:

```powershell
python CampusBot.py --console
```

To compare them fairly, use the same environment variables and prompt, start with a new conversation in each mode, and note the elapsed time until the answer is complete. Keep the Gemini API key private and do not paste it into the report or source code.

## Appendix B — Submission checklist

- [ ] Fill in the student name, roll number, batch/section, and any required submission date.
- [ ] Check the exact title and required report format against the college's current template.
- [ ] Run `python -m unittest -v` and record the actual result; do not report tests as passed unless they were run.
- [ ] Demonstrate both GUI and console modes.
- [ ] Demonstrate offline behavior and, if permitted, a live Gemini response using a valid private key.
- [ ] Explain that the GUI currently waits for the complete response and streaming is listed as future work.
