import csv

import pytest

from storage import add_card, import_csv, init_db


def test_add_card_normalizes_and_skips_duplicates(tmp_path) -> None:
    connection = init_db(tmp_path / "cards.db")

    assert add_card(connection, "  TCP  ", "Transmission Control Protocol", "Reliable")
    assert not add_card(connection, "tcp", "transmission control protocol", "Duplicate")

    row = connection.execute("SELECT front, back, hint FROM cards").fetchone()
    assert row == ("TCP", "Transmission Control Protocol", "Reliable")


def test_csv_import_is_idempotent(tmp_path) -> None:
    path = tmp_path / "cards.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["front", "back", "hint"])
        writer.writeheader()
        writer.writerow({"front": "OSI", "back": "Seven-layer model", "hint": "Networking"})

    connection = init_db(tmp_path / "cards.db")
    assert import_csv(connection, path) == (1, 0)
    assert import_csv(connection, path) == (0, 1)


def test_csv_import_requires_front_and_back(tmp_path) -> None:
    path = tmp_path / "cards.csv"
    path.write_text("front\nTCP\n", encoding="utf-8")
    connection = init_db(tmp_path / "cards.db")

    with pytest.raises(ValueError, match="back"):
        import_csv(connection, path)
