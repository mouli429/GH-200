# Python To‑Do List Web App

A minimal Flask + SQLite to‑do list application with a simple HTML UI.

👉 For a deeper dive into how the app is structured and how requests flow through it, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Features
- Create, read, update, delete tasks
- Mark tasks complete/incomplete
- Stores data in a local SQLite DB under `instance/todo.db`
- Lightweight, no ORMs

## Quickstart (macOS / zsh)

```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tests/run_db_tests.py  # optional: verify data layer
python app.py                 # start the web app on http://127.0.0.1:5000
```

## Project layout
```
.
├── app.py               # Flask app and routes
├── db.py                # SQLite helpers (init, CRUD)
├── templates/
│   ├── base.html
│   ├── index.html
│   └── edit.html
├── static/
│   └── style.css
├── tests/
│   └── run_db_tests.py  # lightweight data-layer tests
├── requirements.txt
└── .gitignore
```

## Configuration
- The app uses a default `SECRET_KEY='dev'`. For production, set an environment variable:
  - `export FLASK_SECRET_KEY='something-secret'`
- Database file lives in `instance/todo.db` (auto‑created).

## Notes
- The tests use only the standard library and can run without installing any packages.
- For production, consider using a real WSGI server (e.g., `gunicorn`) and a managed database.
