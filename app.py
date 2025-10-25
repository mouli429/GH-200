from __future__ import annotations

import os
from typing import Optional
from flask import Flask, render_template, request, redirect, url_for, flash

import db as dbmod


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # Basic config
    secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")
    app.config.update(
        SECRET_KEY=secret_key,
    )

    # Ensure instance folder exists (for SQLite db)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    def db_path() -> str:
        return os.path.join(app.instance_path, "todo.db")

    @app.before_first_request
    def _init_db() -> None:
        dbmod.init_db(db_path())

    @app.get("/")
    def index():
        todos = dbmod.list_todos(db_path())
        return render_template("index.html", todos=todos)

    @app.post("/add")
    def add():
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        if not title:
            flash("Title is required.", "error")
            return redirect(url_for("index"))
        dbmod.add_todo(title=title, description=description, db_path=db_path())
        flash("Task added.", "success")
        return redirect(url_for("index"))

    @app.get("/edit/<int:todo_id>")
    def edit(todo_id: int):
        todo = dbmod.get_todo(todo_id, db_path())
        if not todo:
            flash("Task not found.", "error")
            return redirect(url_for("index"))
        return render_template("edit.html", todo=todo)

    @app.post("/edit/<int:todo_id>")
    def update(todo_id: int):
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        if not title:
            flash("Title is required.", "error")
            return redirect(url_for("edit", todo_id=todo_id))
        ok = dbmod.update_todo(todo_id, title, description, db_path())
        if not ok:
            flash("Task not found.", "error")
        else:
            flash("Task updated.", "success")
        return redirect(url_for("index"))

    @app.post("/toggle/<int:todo_id>")
    def toggle(todo_id: int):
        dbmod.toggle_todo(todo_id, db_path=db_path())
        return redirect(url_for("index"))

    @app.post("/delete/<int:todo_id>")
    def delete(todo_id: int):
        dbmod.delete_todo(todo_id, db_path=db_path())
        flash("Task deleted.", "success")
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
