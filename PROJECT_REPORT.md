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
CampusBot is a command-line conversational chatbot built in Python. When a Gemini API key is configured, it sends the user's message and recent conversation turns to a generative AI model over HTTPS and displays the generated answer. It also demonstrates basic NLP preprocessing, local CSV conversation history, command handling, environment-variable-based secret management, API error handling, and automated tests that mock API responses. It requires Python 3.10 or later and uses only the Python standard library. Live mode requires internet access, a valid API key, model availability, and quota. It is a classroom prototype, not an official source of college information.

## 1. Introduction
Chatbots interact with people through conversational input. NLP concerns computational processing of human language. CampusBot's live mode uses a generative AI service; a limited offline fallback remains available without a key. This allows the report to demonstrate both API-powered conversation and basic NLP helper functions.

## 2. Problem statement
A small chatbot can demonstrate how user text is converted into categories and responses. Because academic information changes, CampusBot avoids inventing dates, fees, or policies and directs users to official college sources.

## 3. Objectives
- Build an interactive Python chatbot.
- Demonstrate tokenization, stop-word removal, synonym mapping, and intent classification.
- Respond to common college-related topics.
- Save conversation history using CSV.
- Validate inputs and test functions automatically.
- Document limitations and future improvements.

## 4. Tools and requirements
**Software:** Python 3.10+, text editor or IDE, terminal, GitHub.  
**Libraries:** json, os, re, urllib, csv, pathlib, datetime, unittest.  
**Hardware:** Computer capable of running Python.  
**Connectivity:** Not required at runtime.

## 5. System design
1. User enters a message.
2. Text is tokenized and normalized to lowercase.
3. Stop words are removed and selected synonyms are mapped.
4. Remaining words are compared with intent keyword sets.
5. The strongest matching intent selects a response; unmatched text receives a fallback.
6. The turn is appended to CSV history.
7. The loop continues until exit.

~~~text
Start → Read message → Validate input → Tokenize / preprocess
     → Match intent → Select response or fallback → Save CSV
     → Continue or exit
~~~

## 6. Module description
- **main.py:** User interface, conversation loop, input validation, history display, recursive word-count helper.
- **nlp_engine.py:** Tokenization, preprocessing, synonym mapping, intent classification, response generation.
- **storage.py:** Appends and reads CSV records.
- **test_chatbot.py:** Automated tests for NLP, validation, recursion, and storage.

## 7. NLP method
**Tokenization:** Regular expressions extract lowercase alphanumeric tokens.  
**Stop-word removal:** Common grammatical words are removed.  
**Synonym mapping:** Alternatives such as “tests” are normalized to “exam”.  
**Intent classification:** Keyword overlaps are counted and the strongest intent is selected.  
**Response generation:** The intent selects a predefined answer; unknown text receives a fallback.

This deterministic rule-based approach is not a generative AI model and does not learn from conversations.

## 8. Python concepts
Variables, strings, lists, sets, dictionaries, loops, conditionals, functions, recursion, modules, exception handling, regular expressions, file handling, CSV, and unit testing.

## 9. Test plan and cases
Run **python -m unittest -v**.

| Test | Expected behavior |
|---|---|
| Tokenization | Lowercase tokens returned |
| Stop words and synonyms | Noise removed; selected synonym normalized |
| Exam / fees / library questions | Correct intent detected |
| Unknown question | Fallback response returned |
| Empty text | No intent returned safely |
| Blank input | User prompted again |
| Word count | Correct count returned |
| CSV round-trip | Stored message can be read back |

**Verified automated test result:** PASS — 10 tests ran successfully with 0 failures and 0 errors on GitHub Actions using Python 3.11.17 on 2026-10-23. See TEST_RESULTS.md for the run link. Repeat the tests on the computer used for the college demonstration.

## 10. Results and discussion
The intended outcome is an interactive console chatbot that categorizes a small set of college questions, returns predefined guidance, and saves local history. The system is explainable because its keywords are explicit. Accuracy is limited by the keyword list, ambiguity, spelling variation, and lack of a trained language model. Confirm tests on the computer used for evaluation.

## 11. Conclusion
CampusBot combines a live generative AI API, conversational context, Python modules, CSV persistence, secret handling, API error management, and automated tests. It is appropriate for a lab demonstration, but requires a valid Gemini API key for generative answers and is not an authoritative source for changing college policies or personal records.

## 12. Future scope
A graphical interface, streaming responses, configurable model selection, retrieval from verified documents, and explicit citations could improve usability.

## 13. References
1. Python Software Foundation, Python 3 Documentation: https://docs.python.org/3/
2. Python Software Foundation, Regular expression operations: https://docs.python.org/3/library/re.html
3. Python Software Foundation, CSV File Reading and Writing: https://docs.python.org/3/library/csv.html
4. Python Software Foundation, unittest framework: https://docs.python.org/3/library/unittest.html

## Viva questions
1. What is a chatbot?
2. What is NLP?
3. Explain tokenization.
4. Why remove stop words?
5. What is an intent?
6. How does synonym mapping help?
7. How are dictionaries used?
8. Why use CSV?
9. What is unit testing?
10. What are keyword-matching limitations?
11. How would you add an intent?
12. Why should the bot not invent exam dates?
