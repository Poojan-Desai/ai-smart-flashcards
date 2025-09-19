# AI Smart Flashcard System

I built a small Streamlit app with a spaced‑repetition schedule (SM‑2 style). I can add cards, review, and score myself from 1–5. There’s also an optional hint button; if no API key is set, it just gives a simple nudge.

## How I run it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Optional: export OPENAI_API_KEY=...
streamlit run app.py
```

## What I learned
Keeping the data model simple (SQLite), and focusing on the review flow first. The SM‑2 tweaks were decent for a first version.

## Notes
- I keep things simple and readable.
- If something feels off, I open an issue and fix it quickly.
