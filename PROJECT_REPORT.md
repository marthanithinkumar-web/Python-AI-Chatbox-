# COURSE END PROJECT REPORT

## CampusBot — AI Chatbot Development Using Python and NLP

**Course:** Essentials of Python Programming Laboratory  
**Academic year:** 2026–2027  
**Branch / year:** CSD, B.Tech II Year  
**Student name:** Martha Nithin Kumar  
**Roll number:** ____________________  
**Batch / section:** ____________________  
**Course instructor:** ____________________  
**Institution:** Vardhaman College of Engineering

> Complete the roll number, batch/section, instructor, and submission details required by the college.

## Certificate

This is to certify that the course-end project entitled **“CampusBot: AI Chatbot Development Using Python and NLP”** is a work submitted by the student named above as part of the requirements for the Python Programming Laboratory course.

**Faculty signature:** ____________________  
**Date:** ____________________

## Acknowledgement

I thank my course instructor and the Department of Computer Science and Design for their guidance and support in completing this project. This project helped me apply Python programming, text processing, basic machine-learning methods, and software testing to a practical chatbot application.

## Abstract

CampusBot is a desktop chatbot developed using Python and Natural Language Processing (NLP). Its main purpose is to demonstrate how a program can process a user's text, identify the likely meaning of a message, and provide a suitable response. The application uses text normalization and tokenization to prepare input, Term Frequency–Inverse Document Frequency (TF-IDF) to represent text as numerical features, and Logistic Regression to classify a message into an intent. Cosine similarity is used as an additional check so the local chatbot can respond cautiously when an input differs from its training examples. A Tkinter graphical interface allows the user to send messages, view replies, clear the current conversation, and view saved chat history. A compact training set is included in the Python source file, so a separate dataset file is not required. As an optional enhancement, the program can request a broader answer from Groq when a user supplies an API key through an environment variable. The main learning focus remains Python programming and NLP; the chatbot can still provide its local responses when the online service is not configured or is unavailable. The project demonstrates text preprocessing, feature extraction, classification, GUI programming, file handling, exception handling, and testing in one compact application.

## Table of Contents

1. Introduction  
2. Objectives  
3. Python and NLP Concepts  
4. System Requirements  
5. System Design and Workflow  
6. Implementation  
7. Testing  
8. Results and Limitations  
9. Conclusion  
10. Future Scope  
11. References

## 1. Introduction

A chatbot is a software application that communicates with users through natural-language messages. A basic chatbot can match a message to known examples and return a stored response. NLP provides techniques for preparing and representing text so a computer can classify or compare it. CampusBot demonstrates these ideas through a Python desktop application. The application uses a small set of labelled example phrases, learns to associate similar phrases with intents, and presents responses in a simple graphical interface.

## 2. Objectives

- Develop a desktop chatbot using Python.
- Apply text normalization and tokenization to user input.
- Convert text into numerical features using TF-IDF.
- Classify messages with Logistic Regression.
- Use text similarity to reduce uncertain local matches.
- Create a simple GUI using Tkinter.
- Save and retrieve chat turns using CSV file handling.
- Test normal input, known topics, empty messages, and unfamiliar questions.
- Provide optional generative answers without making an external API the core of the project.

## 3. Python and NLP Concepts

### 3.1 Python

Python is the primary programming language for the project. Functions organize repeated tasks, classes group chatbot behavior, lists and dictionaries store training examples and responses, and exception handling manages failures. The standard-library modules support the GUI, JSON request formatting, CSV history, environment variables, threading, and HTTP communication.

### 3.2 Text normalization

Normalization converts input to lowercase, removes most punctuation, and reduces repeated whitespace. This helps treat phrases such as “HELLO!” and “hello” consistently.

### 3.3 Tokenization

Tokenization splits a text string into smaller units called tokens, usually words or numbers. Tokens provide the basic units used by the vectorizer.

### 3.4 TF-IDF

TF-IDF stands for Term Frequency–Inverse Document Frequency. It represents each phrase as a numerical vector. Terms that help distinguish one phrase from the collection receive more useful weights. CampusBot uses unigram and bigram features so both individual words and adjacent word pairs can contribute.

### 3.5 Intent classification

An intent is the likely purpose of a message, such as greeting, asking about Python, or asking about tokenization. Logistic Regression is trained on labelled phrases and predicts an intent for new input. The response associated with the predicted intent is then selected.

### 3.6 Cosine similarity and fallback

Cosine similarity compares the direction of text vectors. CampusBot checks similarity against its stored examples and uses a cautious fallback when the message is blank, has no meaningful overlap, or is too dissimilar. This reduces incorrect matches but cannot eliminate them.

### 3.7 Optional generative response

When the environment variable GROQ_API_KEY is configured, the application can send the question and a limited amount of recent conversation context to Groq. This extends the range of questions the chatbot can answer. The API key is not stored in the source file. If the service fails, the program falls back to the local NLP response. This is an extension to the Python/NLP implementation, not the main subject of the project.

## 4. System Requirements

**Hardware:** A standard desktop or laptop computer.

**Software:** Python 3.10 or later, Tkinter (included with most standard Windows Python installations), and scikit-learn. Internet access and a Groq API key are optional and are only needed for online generative answers.

## 5. System Design and Workflow

**Workflow:** User message → text normalization → tokenization → TF-IDF vectorization → Logistic Regression intent prediction → cosine-similarity check → local response. If the optional Groq feature is configured, a generated answer is tried first; otherwise or on failure, the local NLP path is used.

The graphical interface is built with Tkinter. A worker thread handles the answer request so the interface remains responsive. Chat turns are appended to a local CSV file and can be displayed later.

## 6. Implementation

The project is intentionally kept in one main source file, CampusBot.py. The training examples are embedded in the file to avoid a separate data file. The NLPChatbot class builds the TF-IDF representation and trains the Logistic Regression classifier at startup. The normalize_text and tokenize functions prepare input. The predict_intent method predicts a label and similarity score, while local_response selects a stored response or returns an uncertainty message. The generate_response function optionally uses Groq and falls back to local NLP. The Tkinter GUI accepts messages, displays replies, and provides conversation and history controls.

### Algorithm

1. Start the application and load the embedded training examples.
2. Normalize and tokenize the training phrases.
3. Build TF-IDF features and train the intent classifier.
4. Display the chat window.
5. Read a user's message and validate that it is not empty.
6. If Groq is configured, request a generated answer with recent context.
7. If online generation is unavailable or fails, process the message with local NLP.
8. Compare text similarity and choose a stored response or an uncertainty fallback.
9. Display the response and save the conversation turn in CSV format.
10. Continue until the user closes the application.

## 7. Testing

| Test | Input or action | Expected result |
|---|---|---|
| Text normalization | Mixed case and punctuation | Lowercase, cleaned text |
| Tokenization | “Hello NLP 101!” | Word tokens are returned |
| Known intent | “What is Python?” | Python-related intent and response |
| NLP concept | “Explain tokenization” | Tokenization explanation |
| Empty input | Blank message | Request to enter a question |
| Unknown input | Unrelated phrase | Cautious fallback rather than a confident unrelated answer |
| Offline/local mode | No GROQ_API_KEY | Local NLP response path works |
| Chat history | Send messages and reopen history | Turns are stored and readable |
| Online service error | Invalid key or unavailable service | App does not crash; local fallback is attempted |

Automated tests are stored in tests/test_campusbot.py. Run them with: python -m unittest discover -s tests -v

## 8. Results and Limitations

CampusBot demonstrates a working Python GUI and a local NLP pipeline using text preprocessing, TF-IDF, intent classification, similarity checking, and stored responses. It also demonstrates local CSV persistence and graceful fallback behavior. The local model only knows the topics represented by its compact training examples, so it cannot answer every possible question. Classification quality depends on the examples and similarity threshold. Groq answers require internet access, a valid key, model availability, and applicable quota. Generated responses may still be incorrect and should be checked for important decisions.

## 9. Conclusion

The project applies core Python programming and introductory NLP concepts to a practical chatbot. It shows how raw text is normalized, tokenized, transformed into numerical features, classified, and mapped to a response. The Tkinter interface and CSV history add practical application features, while the optional online component illustrates how an existing Python program can be extended without replacing the NLP learning objective.

## 10. Future Scope

- Expand and evaluate the training phrases with a balanced dataset.
- Measure intent-classification accuracy, precision, and recall.
- Add stemming or lemmatization and compare results.
- Improve context handling and local retrieval.
- Add a more detailed evaluation set for unfamiliar and misspelled queries.
- Improve accessibility and GUI layout.

## 11. References

1. Python documentation: https://docs.python.org/3/
2. scikit-learn documentation: https://scikit-learn.org/stable/
3. Natural Language Toolkit book (NLP concepts): https://www.nltk.org/book/
4. Groq documentation (optional integration): https://console.groq.com/docs
