# Verified Test Results

**Repository:** https://github.com/marthanithinkumar-web/Python-AI-Chatbox-  
**Workflow:** CampusBot tests  
**Test command:** python -m unittest -v  
**Coverage:** tokenization, basic preprocessing, greeting intent, unknown-intent handling, honest no-key fallback, mocked Gemini response parsing, quota/rate-limit handling, blank input validation, recursive word count, and CSV history round-trip.

The test suite is designed to run without a real API key and does not consume Gemini quota. Check the latest GitHub Actions run for the current commit's pass/fail status:

https://github.com/marthanithinkumar-web/Python-AI-Chatbox-/actions

Live response quality additionally depends on a valid GEMINI_API_KEY, internet access, enabled model access, and available quota. Run the app locally with a valid key to verify end-to-end live generation.
