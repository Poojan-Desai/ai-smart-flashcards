"""Small, testable SQLite persistence layer for the flashcard app."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from srs import CardState


def init_db(database: str | Path = "flashcards.db") -> sqlite3.Connection:
    connection = sqlite3.connect(database)
    connection.execute(
        """CREATE TABLE IF NOT EXISTS cards(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            hint TEXT,
            interval INT DEFAULT 0,
            repetition INT DEFAULT 0,
            ease REAL DEFAULT 2.5,
            next_review TEXT DEFAULT (datetime('now'))
        )"""
    )
    connection.commit()
    return connection


def add_card(
    connection: sqlite3.Connection, front: str, back: str, hint: str = ""
) -> bool:
    """Add one normalized card, returning False when it already exists."""
    normalized_front = front.strip()
    normalized_back = back.strip()
    if not normalized_front or not normalized_back:
        raise ValueError("front and back are required")

    existing = connection.execute(
        "SELECT 1 FROM cards WHERE lower(front) = lower(?) AND lower(back) = lower(?) LIMIT 1",
        (normalized_front, normalized_back),
    ).fetchone()
    if existing:
        return False

    connection.execute(
        "INSERT INTO cards(front, back, hint, next_review) VALUES(?,?,?,datetime('now'))",
        (normalized_front, normalized_back, hint.strip()),
    )
    connection.commit()
    return True


def import_csv(
    connection: sqlite3.Connection, path: str | Path = "data/flashcards.csv"
) -> tuple[int, int]:
    """Import valid cards once and return (inserted, duplicates_skipped)."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)

    data = pd.read_csv(csv_path).fillna("")
    missing = sorted({"front", "back"} - set(data.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    inserted = 0
    skipped = 0
    for row in data.to_dict(orient="records"):
        if add_card(
            connection,
            str(row["front"]),
            str(row["back"]),
            str(row.get("hint", "")),
        ):
            inserted += 1
        else:
            skipped += 1
    return inserted, skipped


def load_due(connection: sqlite3.Connection):
    return connection.execute(
        """SELECT id, front, back, hint, interval, repetition, ease, next_review
           FROM cards
           WHERE datetime(next_review) <= datetime('now')
           ORDER BY next_review, id
           LIMIT 1"""
    ).fetchone()


def update_card(
    connection: sqlite3.Connection,
    card_id: int,
    state: CardState,
    next_review,
) -> None:
    connection.execute(
        "UPDATE cards SET interval=?, repetition=?, ease=?, next_review=? WHERE id=?",
        (state.interval, state.repetition, state.ease, next_review.isoformat(), card_id),
    )
    connection.commit()
