"""Lightweight tests for db.py using only the standard library.
Run: python tests/run_db_tests.py
"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import db


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, "test.db")
        db.init_db(db_path)

        # Add todos
        a = db.add_todo("Buy milk", "2 liters", db_path=db_path)
        b = db.add_todo("Read book", "Finish chapter 3", db_path=db_path)
        assert isinstance(a, int) and isinstance(b, int)

        todos = db.list_todos(db_path)
        assert len(todos) == 2, f"expected 2 todos, got {len(todos)}"

        # Get and update
        t = db.get_todo(a, db_path)
        assert t and t["title"] == "Buy milk"
        ok = db.update_todo(a, "Buy milk and bread", "Whole grain", db_path)
        assert ok
        t2 = db.get_todo(a, db_path)
        assert t2 and t2["title"] == "Buy milk and bread" and t2["description"] == "Whole grain"

        # Toggle
        ok = db.toggle_todo(a, db_path=db_path)
        assert ok
        t3 = db.get_todo(a, db_path)
        assert t3 and int(t3["done"]) == 1

        # Delete
        ok = db.delete_todo(b, db_path)
        assert ok
        todos = db.list_todos(db_path)
        assert len(todos) == 1

    print("db tests: OK")


if __name__ == "__main__":
    main()
