# Smart Flashcards

An early Streamlit learning project for creating and reviewing flashcards with
a small SQLite database and an SM-2-inspired spaced-repetition scheduler. Users
can add cards, review the next due card, score recall from 1–5, and optionally
request a short study hint.

Card persistence is separated into a testable storage layer. CSV imports are
idempotent: normalized front/back duplicates are skipped and reported instead
of silently creating repeated cards.

The core review workflow works without any paid service. If `OPENAI_API_KEY` is
unset—or a hint request fails—the app uses the card's saved hint or a generic
study prompt. The optional hint is an API-assisted convenience, not the
scheduling engine.

## Architecture

```text
Streamlit interface -> SQLite card store
                    -> SM-2-inspired scheduler
                    -> optional OpenAI hint provider with local fallback
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To enable optional generated hints, copy `.env.example` to `.env`, add your key,
and load it into your shell before starting the app. Never commit `.env`.

## Test

```bash
pip install -r requirements-dev.txt
pytest
```

The tests cover scheduling behavior, storage validation, duplicate prevention,
and repeatable CSV imports.

## Limitations

- SQLite is local and designed for a single user.
- The scheduler is inspired by SM-2; it is not a validated learning study.
- There is no account, sync, or deployment layer.

## Stack

Python, Streamlit, SQLite, pandas, OpenAI's optional Python client, and pytest.
