# Verified Test Results

**Repository:** https://github.com/marthanithinkumar-web/Python-AI-Chatbox-  
**Workflow:** CampusBot tests  
**Test command:** `python -m unittest -v`  
**Latest verified run:** https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/actions/runs/39956294000  
**Result:** PASS — GitHub Actions completed successfully on 2026-10-23.

The suite covers tokenization, basic preprocessing, intent handling, honest no-key fallback, mocked Gemini response parsing, quota/model error handling, blank input validation, recursive word count, CSV history round-trip, and the new GUI response/context integration and recent-context limit. The tests use mocked responses and do not consume Gemini API quota.

The CI pass verifies Python-level tests and GUI response integration logic. It does **not** launch an interactive desktop window or prove live Gemini availability on every computer. Before demonstrating, run `run_gui.bat` on Windows, send a question, test a follow-up, clear the conversation, view saved history, and run `run_tests.bat`.

Live AI availability and answer quality depend on a valid `GEMINI_API_KEY`, internet access, model access, and available quota.
