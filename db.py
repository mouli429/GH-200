from __future__ import annotations

import sqlite3
from typing import Iterable, List, Optional, Dict, Any

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    with _connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


def add_todo(title: str, description: str = "", db_path: str = "todo.db") -> int:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO todos (title, description) VALUES (?, ?)", (title, description)
        )
        conn.commit()
        return int(cur.lastrowid)


def list_todos(db_path: str = "todo.db") -> List[Dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, title, description, done, created_at FROM todos ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_todo(todo_id: int, db_path: str = "todo.db") -> Optional[Dict[str, Any]]:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, title, description, done, created_at FROM todos WHERE id = ?",
            (todo_id,),
        ).fetchone()
        return dict(row) if row else None


def update_todo(
    todo_id: int, title: str, description: str = "", db_path: str = "todo.db"
) -> bool:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "UPDATE todos SET title = ?, description = ? WHERE id = ?",
            (title, description, todo_id),
        )
        conn.commit()
        return cur.rowcount > 0


def toggle_todo(todo_id: int, done: Optional[bool] = None, db_path: str = "todo.db") -> bool:
    with _connect(db_path) as conn:
        if done is None:
            row = conn.execute("SELECT done FROM todos WHERE id = ?", (todo_id,)).fetchone()
            if not row:
                return False
            new_done = 0 if int(row[0]) else 1
        else:
            new_done = 1 if done else 0
        cur = conn.execute("UPDATE todos SET done = ? WHERE id = ?", (new_done, todo_id))
        conn.commit()
        return cur.rowcount > 0


def delete_todo(todo_id: int, db_path: str = "todo.db") -> bool:
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        return cur.rowcount > 0
