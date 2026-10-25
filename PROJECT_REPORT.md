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

> Fill in the roll number, batch/section, submission date, and any college-required fields before submitting.

## Certificate

This is to certify that the course end project entitled “CampusBot: AI Chatbot Development Using Python and NLP” has been carried out by Martha Nithin Kumar as part of the requirements for Essentials of Python Programming Laboratory (A9514) during the academic year 2026–2027.

Course Instructor: ____________________  
Head of the Department: ____________________  
Date: ____________________

## Declaration

I declare that this report describes the CampusBot project and its implementation to the best of my knowledge. External technical resources used for implementation are acknowledged in the references.

Signature: ____________________  
Date: ____________________

## Acknowledgement

I express my sincere gratitude to Mr. B. Nagulu, course instructor, and the Department of Computer Science and Engineering (Data Science), Vardhaman College of Engineering, for the guidance and opportunity to undertake this project.

## Abstract

CampusBot is a desktop chatbot developed in Python to demonstrate fundamental Natural Language Processing techniques. The application uses Tkinter for its graphical interface and a local intent dataset stored in JSON. At startup, it normalizes and tokenizes example phrases, converts them into TF-IDF vectors using unigram and bigram features, and trains a Logistic Regression classifier to identify the likely intent of a user's message. Cosine similarity is used as an additional check against stored examples; when a message is too dissimilar, the chatbot returns a fallback message rather than pretending to understand. Replies are selected from responses defined for the predicted intent. Conversation exchanges can be saved to a local CSV file. This configuration does not use Groq, a hosted language model, Flask, or an external API, so chat processing can continue offline after Python and scikit-learn have been installed. The system is an educational intent-based chatbot, not a generative model. Its coverage depends on the quality and range of examples in the dataset. Unit tests cover preprocessing, intent prediction, fallback behaviour, and history storage.

**Keywords:** Python, Natural Language Processing, TF-IDF, Logistic Regression, cosine similarity, Tkinter, chatbot, text classification.

## 1. Introduction

A chatbot communicates with users through natural language. Exact keyword systems may fail when users phrase questions differently. An NLP-based chatbot can represent example phrases numerically and classify messages into likely intents. CampusBot demonstrates this process with Python and scikit-learn in a small, explainable college project.

## 2. Problem Statement and Objectives

### 2.1 Problem Statement

Users express the same question in different ways. A chatbot that relies only on exact phrase matches may fail when wording changes. This project uses text features and a supervised classifier to map messages to known intents and uses similarity checking to provide a fallback for unrelated messages.

### 2.2 Objectives

- Build a desktop chatbot using Python and Tkinter.
- Demonstrate text normalization and tokenization.
- Represent text with TF-IDF unigram and bigram features.
- Train a Logistic Regression model to classify intents.
- Use cosine similarity to help detect out-of-scope messages.
- Store patterns and responses in an editable JSON file.
- Save conversation history locally in CSV format.
- Test preprocessing, predictions, fallback behaviour, and history storage.
- Avoid external AI APIs and hosted services.

## 3. Requirements and Feasibility

| Component | Technology / purpose |
|---|---|
| Language | Python 3.10+ |
| GUI | Tkinter |
| Feature extraction | scikit-learn TfidfVectorizer |
| Classifier | scikit-learn LogisticRegression |
| Similarity | Cosine similarity |
| Dataset | intents.json |
| History | Local CSV |
| Testing | Python unittest |

A regular laptop or desktop capable of running Python and a graphical desktop environment is sufficient. The project does not require a GPU or dedicated AI server. Install Python dependencies before first use; chat processing is local afterwards.

## 4. System Architecture

```text
User
  -> Tkinter desktop chat interface
  -> text normalization and tokenization
  -> TF-IDF vectorization (unigrams + bigrams)
  -> Logistic Regression intent classifier
  -> cosine-similarity check
  -> local response from intents.json
  -> display answer and append to CSV history
```

### 4.1 Request Flow

1. The user enters a message.
2. Text is lowercased and unsupported punctuation is removed.
3. Tokenization extracts word tokens.
4. TF-IDF converts the message into numeric features.
5. Logistic Regression predicts an intent using labelled examples.
6. Cosine similarity compares the message with training patterns.
7. Low similarity triggers a fallback; otherwise a response is selected from the predicted intent.
8. The answer is displayed and the exchange is written to local history when possible.

## 5. NLP Concepts

### 5.1 Normalization and Tokenization

Normalization makes text consistent, for example “HELLO, Python!!” becomes “hello python”. Tokenization splits a sentence into units. “Hello NLP 101!” becomes ["hello", "nlp", "101"].

### 5.2 TF-IDF

TF-IDF means Term Frequency–Inverse Document Frequency. It converts phrases to weighted numeric vectors, assigning useful weights to terms that distinguish examples. This project uses unigrams and bigrams.

### 5.3 Logistic Regression

Logistic Regression is a supervised classification algorithm. It is trained on example phrases labelled with intent tags. For a new message, it predicts one of the known intent classes; it does not create new facts or new intents automatically.

### 5.4 Cosine Similarity

Cosine similarity compares the direction of numeric vectors. CampusBot compares a message with stored examples and uses a threshold to reject very dissimilar input. This is a heuristic, not a guarantee of correctness.

### 5.5 Intent Dataset

Each item in intents.json contains a unique tag, sample patterns, and possible responses. New topics can be added by editing the dataset and restarting the application.

## 6. Implementation

CampusBot.py loads the dataset, normalizes and tokenizes example phrases, trains TF-IDF and Logistic Regression, and creates the Tkinter window. User messages are processed locally. No request is sent to Groq or another server. Conversation history is appended to chat_history.csv with a timestamp, user message, and response.

Example dataset entry:

```json
{
  "tag": "python_definition",
  "patterns": ["what is python", "define python", "explain python"],
  "responses": ["Python is a high-level, general-purpose programming language."]
}
```

### 6.1 Run the Project

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python CampusBot.py
```

On Windows, run_gui.bat can launch the GUI after installing dependencies. Ensure Tkinter/Tcl-Tk is available.

## 7. Testing and Results

| ID | Test | Expected behaviour |
|---|---|---|
| TC01 | Normalize uppercase text and punctuation | Consistent lowercase text |
| TC02 | Tokenize a sentence | Expected word tokens |
| TC03 | Ask “what is Python” | python_definition intent |
| TC04 | Ask about NLP | nlp_definition intent |
| TC05 | Ask about tokenization | Relevant local response |
| TC06 | Empty input | Prompt to type a message |
| TC07 | Unrelated question | Fallback response |
| TC08 | Train a custom dataset | Sample maps to its intent |
| TC09 | Save/read CSV history | Rows and headers are preserved |

Run after installing requirements:

```powershell
python -m py_compile CampusBot.py tests/test_campusbot.py
python -m unittest discover -s tests -v
```

Record the actual test output after running the commands on the submission machine. Do not claim tests passed unless the run confirms it. The design demonstrates a workflow from raw text to a predicted intent and selected response. Prediction quality must be evaluated on held-out examples before making quantitative accuracy claims.

## 8. Privacy, Limitations and Future Scope

Messages are processed locally and are not uploaded to a remote API. Conversation history is stored in a local, unencrypted CSV file, so do not enter confidential information. The chatbot only recognises topics represented in its dataset; similar wording can be assigned to the wrong intent, and its responses are predefined rather than generated by a general language model. Future improvements include expanding examples, reporting precision/recall/F1 on held-out data, adding local FAQ retrieval, and comparing optional stemming or lemmatization.

## 9. Conclusion

CampusBot demonstrates NLP through normalization, tokenization, TF-IDF feature extraction, Logistic Regression intent classification, and cosine-similarity checking. It uses a local JSON dataset and stores history in CSV. This configuration has no hosted AI backend or external API and can process messages offline after setup. Its coverage and accuracy depend on the quality of the labelled examples.

## References

1. Python Software Foundation, Python Documentation: https://docs.python.org/3/
2. scikit-learn, Working With Text Data: https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html
3. scikit-learn, TfidfVectorizer: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
4. scikit-learn, LogisticRegression: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
5. scikit-learn, cosine_similarity: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html
6. Python Software Foundation, Tkinter: https://docs.python.org/3/library/tkinter.html

## Appendix A — Viva Questions

1. What is Natural Language Processing?
2. What is normalization?
3. What is tokenization?
4. What does TF-IDF stand for?
5. Why use TF-IDF vectors?
6. What is Logistic Regression?
7. What is an intent?
8. What does cosine similarity measure?
9. Why use a fallback response?
10. What is intents.json used for?
11. How does this project differ from a Groq-powered chatbot?
12. Why does it work offline after installation?
13. What are the limitations of a predefined intent dataset?
14. How can precision, recall, and F1-score evaluate a classifier?
