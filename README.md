# CampusBot — Python + NLP Chatbot

CampusBot is a local desktop chatbot built with Python, Tkinter, and classical Natural Language Processing. It uses TF-IDF features and Logistic Regression to classify a message into an intent, checks similarity against known examples, and chooses a response from a local dataset.

**No Groq, hosted language model, Flask backend, API key, or internet connection is needed while chatting.** Install the Python dependency once first.

## Features

- Desktop chat interface with Send and Enter-to-send
- Text normalization and tokenization
- TF-IDF vectorization with unigram and bigram features
- Logistic Regression intent classification
- Cosine-similarity check and fallback for unknown questions
- Editable intent and response dataset in intents.json
- Local CSV conversation history
- No remote service or secret key
- Unit tests

## Requirements

- Python 3.10 or newer
- Tkinter (normally included with Windows Python; ensure Tcl/Tk is selected)
- scikit-learn and its dependencies

## Run on Windows

Open PowerShell in the repository folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python CampusBot.py
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`, or install packages without activating a virtual environment. You can also double-click run_gui.bat after installing requirements.

## How the NLP pipeline works

1. Normalize: lowercase text and remove unsupported punctuation.
2. Tokenize: split the message into word tokens.
3. Vectorize: convert example phrases into TF-IDF vectors using unigrams and bigrams.
4. Classify intent: Logistic Regression predicts a label such as greeting, python_definition, or nlp_definition.
5. Check similarity: cosine similarity compares the new message to training examples. Low similarity triggers a fallback.
6. Respond: choose a response from the matching intent in intents.json.

The model trains from the local JSON dataset when the app starts. It does not generate new knowledge like a large language model. Coverage depends on the examples, so add varied phrasings and test unfamiliar questions.

## Teach CampusBot new topics

Edit intents.json. Each intent needs a unique tag, a list of patterns, and a list of responses. Add the intent to the top-level intents array, then restart CampusBot so it retrains the model. Use many natural phrasings per intent and avoid identical patterns assigned to different labels.

## Tests

```powershell
python -m py_compile CampusBot.py tests/test_campusbot.py
python -m unittest discover -s tests -v
```

Tests check preprocessing, known-intent predictions, fallback behaviour, and CSV history. Run them where requirements.txt has been installed.

## Project report

See PROJECT_REPORT.md. Fill in roll number, batch/section, date, and other college-required fields before submitting.

## Privacy and limitations

Messages and replies are saved to chat_history.csv beside the program. The file is local and not encrypted; do not enter confidential information. CampusBot does not upload messages. It is an educational intent-classification project, not a general-purpose generative AI assistant; it may misunderstand out-of-scope questions.
