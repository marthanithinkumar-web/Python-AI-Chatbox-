# Project Outcomes — CampusBot

## Aim
Build a Python chatbot that demonstrates introductory NLP and rule-based conversational interaction.

## Expected learning outcomes
1. Explain the purpose of a chatbot and a basic NLP preprocessing pipeline.
2. Normalize text with case folding, tokenization, stop-word removal, and synonym mapping.
3. Classify messages using keyword overlap and map intents to responses.
4. Organize an application into reusable functions and modules.
5. Read and write structured conversation records using CSV.
6. Apply input validation, exception handling, and unit testing.
7. Explain limitations of rule-based systems, ambiguity, and limited vocabulary.
8. Run a Python project and tests from a terminal.

## Demonstration checklist
- [ ] Start with python main.py.
- [ ] Test hello, when is the exam date, when are the tests, and tell me about library books.
- [ ] Test unknown text: quantum banana spaceship.
- [ ] Enter history and show saved turns.
- [ ] Enter exit.
- [ ] Run python -m unittest -v and record the actual result.

## Evaluation
The tests cover tokenization, stop words, synonym normalization, intent detection, fallback, blank input, recursion, and CSV persistence. GitHub Actions repeats the test command on pushes and pull requests. Record a pass percentage only after an actual successful test run.

## Limitations
Keyword matching is not a trained neural model. The chatbot has no live college data. Ambiguous messages may be misclassified. CSV history is local and not encrypted; use sample data only.

## Future scope
A GUI, multilingual support, editable FAQ data, TF-IDF similarity, and a verified official college FAQ source could be added later.
