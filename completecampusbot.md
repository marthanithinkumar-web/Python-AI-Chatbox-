# completecampusbot — Complete CampusBot Project Handoff
**Prepared:** 25 October 2026  
**Purpose:** Source-grounded handoff for Claude AI. This document separates current GitHub evidence from historical project chats and unverified runtime claims.

## Project identity and priorities
- **Title:** CampusBot — AI Chatbot Development Using Python and NLP.
- **Repository:** https://github.com/marthanithinkumar-web/Python-AI-Chatbox-
- **Branch:** main. **Main application:** `CampusBot.py`.
- College end-semester Python lab project; prior context says B.Tech II Year, CSD, academic year 2026–2027.
- User priority: **Python first, NLP second, optional Groq/API third**.
- Keep one clear main entry point, retain the project report, keep sufficient examples to demonstrate NLP, avoid unnecessary duplicate application files, preserve GUI design/dimensions, and verify before claiming success.
- Do not commit API keys. Clearly distinguish GitHub changes from the user's local Windows copy.

## Executive finding: source and documentation disagree
On 25 October 2026, current main was fetched directly:
- `CampusBot.py` blob SHA: `dad47c1b80cf46065664174db3ac18195a8defa3`.
- Latest inspected commit: `2c3b8612e03e739c23a65cb6b33fae49fae6c098` — “Handle empty NLP intent rules without crashing” (2026-10-25 14:49:07 UTC).
- Current app has Tkinter GUI, a lightweight dictionary/phrase-based local `analyze_text()`, CSV history, and HTTP client for a shared backend.
- Current app does **not** contain `NLPChatbot`, TF-IDF, Logistic Regression, cosine-similarity classification, direct Groq calls, or direct Gemini calls.
- `README.md`, `PROJECT_REPORT.md`, `requirements.txt`, and `tests/test_campusbot.py` still describe a previous/intended TF-IDF + Logistic Regression + cosine-similarity + optional Groq architecture. Tests expect names absent from current source and are likely incompatible.
- This was source inspection only: no compile, unit tests, GUI launch, live backend call, Groq, or Gemini test was run in this audit.

Links:
- [Current CampusBot.py](https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/blob/main/CampusBot.py)
- [README.md](https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/blob/main/README.md)
- [PROJECT_REPORT.md](https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/blob/main/PROJECT_REPORT.md)
- [tests/test_campusbot.py](https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/blob/main/tests/test_campusbot.py)
- [Latest inspected commit](https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/commit/2c3b8612e03e739c23a65cb6b33fae49fae6c098)

## Requirements and decisions from prior project chats
1. Keep `CampusBot.py` as the one main application entry point. Remove duplicates only after checking imports, tests, launchers, workflows and references.
2. Keep the report in the repository and focus it on Python and NLP, not API/Groq/Render.
3. Retain enough training examples/data to demonstrate the NLP learning outcomes.
4. Keep implementation explainable for a college demo/viva.
5. Preserve the GUI layout and dimensions unless there is a verified reason to change them: 850×680, minimum 560×460.
6. The user previously said the initial chatbot responses were weak and wanted a more useful, real-time-feeling chatbot.
7. User needs actual repository changes and clear confirmation; a GitHub update does not automatically change a downloaded local file.
8. Keep credentials out of source and commits.

## Historical timeline from chats
- **23 Oct — Gemini version:** Earlier version was described as a Windows console/desktop chatbot using Gemini. `gemini-2.5-flash` was reported unavailable; prior chat says a response was received after changing `GEMINI_MODEL` to `gemini-3.5-flash-lite`. Historical only; current main has no Gemini key/model or direct Gemini request.
- **23 Oct — single-file app:** A simplified `CampusBot.py` was discussed with GUI, conversation context, NLP helpers, AI, and CSV history. A Tkinter `pady` startup error was discussed; prior fix was integer padding in Frame constructors and tuple padding on `.pack()`. Current main uses integer Frame padding and tuple padding in pack calls.
- **25 Oct — focus:** User asked for one necessary main file, no unnecessary files/data, report retained, Python/NLP focus, optional Groq/API third, and sufficient examples.
- **25 Oct — missing constant:** After the user removed `hi` from NLP, error appeared: `Unexpected application error: name 'INTENT_KEYWORDS' is not defined`. Likely the whole dictionary assignment was removed/renamed rather than only the item. Current main defines `INTENT_KEYWORDS` and includes `hi` under greeting. If removing it, remove only the string from the set, not the dictionary itself.
- **25 Oct — code safeguards:** Commits expanded dictionaries, guarded missing constants and fixed empty intent rules.
- **25 Oct — latest review:** Source was fetched and discrepancies between source, report, README and tests were identified.

## Current main implementation, verified from source
### Imports and configuration
- Standard library: `csv`, `json`, `os`, `queue`, `re`, `unicodedata`, `threading`, `urllib.error`, `urllib.request`, `datetime/timezone`, `pathlib.Path`. Tkinter is imported inside `run_gui()`.
- `APP_NAME = "CampusBot"`.
- `BACKEND_URL` reads `CAMPUSBOT_BACKEND_URL`; default is `https://campusbot-ai-backend.onrender.com`.
- `HISTORY_FILE` is `chat_history.csv` next to the source file.

### Local NLP
Dictionaries/constants: `NLP_STOP_WORDS`, `POSITIVE_WORDS`, `NEGATIVE_WORDS`, `NEGATION_WORDS`, `INTENSIFIERS`, `INTENT_PHRASES`, `INTENT_KEYWORDS`, `QUESTION_STARTERS`.

`analyze_text(text)`:
1. Applies Unicode NFKC normalization, casefolding and trimming.
2. Tokenizes with a Unicode-aware regex, preserving internal apostrophes; curly apostrophes are normalized.
3. Removes stop words, selected contractions and single-character tokens for meaningful-token analysis.
4. Counts tokens and creates adjacent two-word phrase candidates.
5. Ranks phrases/tokens by occurrence/position and returns up to eight unique keywords/phrases.
6. Scores intent from manually defined phrase and keyword dictionaries. A troubleshooting phrase has priority; otherwise the first matching phrase intent wins, then the highest keyword score. With no matching rule it returns generic `question` or `general`.
7. Computes basic lexicon sentiment. A positive/negative word preceded by a negation within three tokens is polarity-flipped; an intensifier within two tokens doubles weight.
8. Labels question type from the first word (who/what/when/where/why/how/which/whose/whom) or punctuation.
9. Returns fields `nlp_tokens`, `nlp_keywords`, `nlp_intent`, `nlp_question_type`, `nlp_sentiment`.

Limitations: this is hand-authored rule/keyword analysis, not a learned classifier. Dictionary order and overlapping categories affect labels. Sentiment heuristics can misread negation scope, sarcasm and complex sentences. Intent is metadata/logging only; it does not choose the actual answer. Repeated `phrase_candidates.count()` can be quadratic for long messages, though chat messages are usually short.

### Backend answer path
- `generate_response(text, history=None, timeout=60)` POSTs JSON `{message, history}` to `BACKEND_URL.rstrip("/") + "/chat"`.
- Message is capped at 12,000 characters; outgoing history is bounded to the last eight entries.
- Expects a non-empty JSON `reply`.
- Handles HTTP errors, network/timeouts, OS errors and JSON/type/value problems with user-facing fallback messages.
- Current desktop source contains no `GROQ_API_KEY`, `GROQ_MODEL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, scikit-learn import or provider SDK. Do not claim direct Groq/Gemini calls. Provider setup would need to be verified in the backend source/configuration.
- Local `analyze_text()` does not generate an offline answer. Current desktop answer path depends on remote backend availability.

### CSV, history and GUI
- `append_chat()` calls NLP defensively and writes timestamp, user, bot, tokens, keywords, intent, question type and sentiment to CSV. It attempts to migrate old CSV headers.
- `read_history()` reads CSV rows; `add_turn()` adds user/model turns and keeps the last 12 context items.
- Tkinter window title: `CampusBot - AI Chatbot`; geometry 850×680; minimum 560×460.
- GUI has scrollable chat, input, Send, Clear conversation, Show saved history, status and a reminder not to enter passwords/API keys.
- Enter submits; Send is disabled while busy. Clear clears in-memory context but retains CSV history. History view shows latest ten exchanges.
- Worker thread makes request; queue + `root.after(100, self.poll)` updates UI.
- `append_chat()` catches NLP errors and uses safe neutral metadata. Background caller catches history-writing errors so a valid reply should not be discarded. Direct file operations can still raise on I/O failure, so test these paths.

## NLP concepts and intended coursework emphasis
The project should explain Python functions, dictionaries/lists, text normalization, tokenization, stop-word filtering, phrase/key-term extraction, rule-based intent classification, lexicon sentiment, question-type detection, CSV file handling, exception handling, threads/queues and Tkinter GUI programming. If the final architecture restores TF-IDF/Logistic Regression, explain those accurately and retain sufficient labelled training examples. Do not describe TF-IDF, Logistic Regression, cosine similarity or offline local response as implemented unless they are actually present in the final source.

## Repository inconsistency audit
| File | Current observation | Needed action |
|---|---|---|
| `CampusBot.py` | Tkinter + dictionary NLP metadata + shared backend HTTP client + CSV history | Keep as entry point unless user approves architecture change |
| `README.md` | Claims TF-IDF, Logistic Regression, cosine similarity, optional direct Groq and local fallback | Update to actual implementation or restore intended ML architecture |
| `PROJECT_REPORT.md` | Claims `NLPChatbot`, embedded training examples, TF-IDF, Logistic Regression, cosine similarity, Groq and offline local answers | Materially inconsistent; revise after architecture decision |
| `tests/test_campusbot.py` | Expects `NLPChatbot`, `normalize_text`, `tokenize`, `_bot`, `groq_response`, `local_response` | Likely fails because these names are absent; rewrite tests or restore architecture |
| `requirements.txt` | `scikit-learn>=1.4,<2.0` | Current source does not import sklearn; remove if unused or retain if ML pipeline is restored |
| `run_gui.bat` | Runs `python CampusBot.py`, then `py CampusBot.py` | Consistent with current entry point |
| `run_tests.bat` | Compiles source/tests then runs unittest discovery | Commands reasonable, test expectations are mismatched |

## Recent commits inspected
- `55b4ce9f00c8ef67a18bc684cf6560be7a7bf047` — “Expand local NLP analysis dictionaries without changing UI or backend”.
- `ff404d2dfc6c5a4a42edc7217f263ab54ff1f4f6` — “Make NLP analysis failures non-blocking for AI replies”.
- `2c3b8612e03e739c23a65cb6b33fae49fae6c098` — “Handle empty NLP intent rules without crashing”.
- Latest inspected commit: https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/commit/2c3b8612e03e739c23a65cb6b33fae49fae6c098

## Issues discussed and current status
| Issue | Status |
|---|---|
| `INTENT_KEYWORDS` NameError | Current source guards missing dictionaries and defines the constant; source-inspected only, not runtime-tested |
| Removing `hi` | Current main still includes `hi`; remove only item if desired, not dictionary assignment |
| Tkinter `pady` geometry error | Current main uses integer Frame padding; tuple padding is on pack calls |
| Missing scikit-learn under Python 3.13 | Current app doesn't import it but requirements still includes it; architecture/dependencies must be aligned |
| Gemini model unavailable | Historical issue; user reported `gemini-3.5-flash-lite` worked after `gemini-2.5-flash` failed |
| Weak answers | Current answer quality depends on backend; local metadata NLP does not answer questions |
| Local copy differs from GitHub | Always specify whether change is remote or local; updating GitHub doesn't replace a downloaded Windows copy |

## Verification status as of this audit
| Check | Status |
|---|---|
| Fetch current main source | Done; SHA above |
| Missing/empty dictionary guards | Present by source inspection |
| GUI geometry | Present by source inspection |
| Backend URL/endpoint | Present by source inspection |
| README/report/tests consistency | Mismatch found |
| Python compile | Not run |
| Automated tests | Not run; likely incompatible |
| Windows GUI launch | Not verified |
| Live backend reply | Not verified |
| Groq/Gemini current integration | Not verified; direct calls absent from desktop source |

## Recommended plan for Claude
1. Re-fetch latest main and inspect all files/history before editing.
2. Choose one coherent architecture matching Python-first, NLP-second priorities. For coursework, consider an explainable local NLP pipeline with labelled examples, TF-IDF, Logistic Regression and uncertainty handling, with optional remote generation secondary **only if implemented and testable**. Alternatively retain current backend client and accurately document dictionary-based metadata NLP plus remote answers.
3. Keep one main entry point and delete files only after checking references.
4. Align dependencies with imports; no scikit-learn if unused, include it if ML is restored.
5. Rewrite tests to match actual functions. Test missing/empty dictionaries, greetings, question types, Unicode/punctuation, sentiment negation, empty input, network errors/timeouts, CSV history and preservation of replies when history logging fails.
6. Mock HTTP calls in ordinary unit tests; no real API key should be required. Never expose secrets.
7. Verify Tkinter startup and preserve GUI geometry.
8. Test the backend separately with a safe prompt; check provider configuration from backend source rather than assuming Groq/Gemini.
9. Align source, README, report, requirements and tests.
10. Run `python -m py_compile CampusBot.py tests/test_campusbot.py` and `python -m unittest discover -s tests -v`; record exact outputs. If unable to run, state why.
11. Commit minimal changes, re-fetch main and verify the final commit.
12. Give exact GitHub links and distinguish repository edits from the user's local Windows copy.

## Acceptance criteria
- Windows GUI launches without geometry errors.
- Message submission returns a visible answer through the intended path.
- Missing/empty NLP rules cannot suppress a valid reply.
- HTTP/network/timeout/invalid JSON failures show useful errors.
- No claim of offline generative answers without actual local answer code.
- GUI geometry remains unchanged unless a minimal fix is necessary.
- CSV history works; history failures don't discard a received reply.
- Tests match code and run without external credentials.
- README, report, requirements, tests and code agree.
- Python and NLP remain the main coursework story; API integration stays secondary.
- No secrets committed.

## Prompt to paste into Claude
You are continuing my college end-semester Python lab project, CampusBot — “AI Chatbot Development Using Python and NLP”.

Repository: https://github.com/marthanithinkumar-web/Python-AI-Chatbox-
Branch: main. Main file: CampusBot.py.
Read this complete handoff first, then re-fetch and inspect latest source.

Priorities: Python first, NLP second, optional Groq/API third. Keep one main entry point, retain the report, preserve enough training examples, and do not redesign the Tkinter GUI (850×680; minimum 560×460) without verified need.

Verified discrepancy: current main CampusBot.py is a Tkinter client with lightweight dictionary/phrase-based analyze_text() metadata, CSV history, and POST to https://campusbot-ai-backend.onrender.com/chat (or CAMPUSBOT_BACKEND_URL). It does not currently implement NLPChatbot, TF-IDF, Logistic Regression, cosine similarity, direct Groq or Gemini described in README.md, PROJECT_REPORT.md and tests/test_campusbot.py. Tests expect missing symbols and are likely incompatible. Latest inspected commit: 2c3b8612e03e739c23a65cb6b33fae49fae6c098. Earlier error: name 'INTENT_KEYWORDS' is not defined; current source guards missing/empty dictionaries but has not been runtime-tested.

Inspect all files/history; choose one coherent architecture; align code, requirements, tests, README and report; write unit tests with mocked network and no required API key; run compile and tests and report exact results; verify live backend/provider separately without exposing secrets; make minimal necessary changes and commit; re-fetch and verify final branch. Never claim tests, GUI, backend, Groq or Gemini works unless actually tested. Clearly distinguish GitHub changes from my local Windows copy.

## Caution
This is a source-audit handoff, not a claim that the project is fixed. No compile, unit test, GUI launch, live API request or provider test was performed in this audit. Re-check the live repository and treat current code as source of truth; do not describe historical TF-IDF/Groq/Gemini features as current unless present in re-fetched code.
