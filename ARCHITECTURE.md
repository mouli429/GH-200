# Application Architecture and Flow

This document explains the structure, components, and request flows of the GH-200 to‑do list application.

- Runtime: Python 3.x
- Framework: Flask 2.2.5 (pinned)
- Templating: Jinja2
- Database: SQLite (file at `instance/todo.db`)
- Frontend: Server-rendered HTML + CSS (no JS framework)

> Note: Flask is pinned to 2.2.5 to retain the `before_first_request` hook used for DB initialization. On Flask 3.x, this hook is removed; see “Alternatives to `before_first_request`” below for migration options.

## High-level architecture

```
+--------------------------+        +------------------+
|        Browser           | <----> |   Flask (app.py) |
|  (HTML forms & links)    |        |  Routes/Views    |
+------------+-------------+        +---------+--------+
             |                                |
             | render_template()               | calls CRUD helpers
             v                                v
        +----+----+                    +------+------+
        | Jinja2  |                    |   db.py    |
        | (HTML)  |                    | SQLite ops |
        +----+----+                    +------+------+
                                          |
                                          v
                                    +-----+-----+
                                    |  SQLite   |
                                    |  todo.db  |
                                    +-----------+
```

## Project structure

- `app.py`: Flask app factory and routes for list/add/edit/toggle/delete; flashes messages and renders templates.
- `db.py`: SQLite data access helpers; each function opens a short‑lived connection (context manager), executes SQL, returns Python data.
- `templates/`: `base.html` (layout), `index.html` (list & add form), `edit.html` (edit form).
- `static/style.css`: Minimal styling.
- `tests/run_db_tests.py`: Lightweight, stdlib‑only verification of `db.py` CRUD behavior.
- `instance/`: Per‑app writable directory for `todo.db` (auto-created by Flask when needed).

## Data model

Single table: `todos`

- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `title TEXT NOT NULL`
- `description TEXT`
- `done INTEGER NOT NULL DEFAULT 0` (0 = incomplete, 1 = complete)
- `created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP`

## Initialization lifecycle

- `create_app()` constructs the Flask app with `instance_relative_config=True`.
- Ensures `app.instance_path` exists (holds the SQLite DB file).
- `@app.before_first_request` invokes `db.init_db(db_path)` to create the `todos` table if it doesn’t exist.
- The app uses `SECRET_KEY` (default `'dev'`, override via `FLASK_SECRET_KEY`).

## Routes and responsibilities

- `GET /` → List tasks
  - Calls `db.list_todos(db_path)` → returns list of dicts
  - Renders `templates/index.html`

- `POST /add` → Create a task
  - Validates non-empty `title` (trims)
  - Calls `db.add_todo(title, description, db_path)`
  - Flashes feedback; redirects to `/`

- `GET /edit/<int:todo_id>` → Show edit form
  - Calls `db.get_todo(todo_id, db_path)`
  - If missing, flash + redirect to `/`
  - Renders `templates/edit.html`

- `POST /edit/<int:todo_id>` → Update a task
  - Validates non-empty `title`
  - Calls `db.update_todo(todo_id, title, description, db_path)`
  - Flash success/error; redirect to `/`

- `POST /toggle/<int:todo_id>` → Toggle completion
  - Calls `db.toggle_todo(todo_id, db_path=db_path)`
  - Redirect to `/`

- `POST /delete/<int:todo_id>` → Delete a task
  - Calls `db.delete_todo(todo_id, db_path)`
  - Flash success; redirect to `/`

## Request flows (sequence)

Add task (POST /add):
```
Browser form -> Flask /add -> validate -> db.add_todo() -> flash -> redirect /
                                             |
                                             v
                                         SQLite INSERT
```

Toggle task (POST /toggle/<id>):
```
Browser checkbox -> Flask /toggle/<id> -> db.toggle_todo() -> redirect /
                                           |
                                           v
                                       SQLite UPDATE
```

Edit task (GET+POST /edit/<id>):
```
GET /edit/<id> -> db.get_todo() -> render edit.html
POST /edit/<id> -> validate -> db.update_todo() -> flash -> redirect /
```

Delete task (POST /delete/<id>):
```
POST /delete/<id> -> db.delete_todo() -> flash -> redirect /
```

## Data access layer (db.py)

- All functions accept an explicit `db_path` (defaults to `todo.db`) to keep them pure and testable.
- Connections are short‑lived (context managers) with `sqlite3.Row` mapping for dict‑like access.
- SQL is simple and parameterized to avoid injection.

Key functions:
- `init_db(db_path)` → create tables
- `add_todo(title, description, db_path)` → returns `lastrowid`
- `list_todos(db_path)` → returns `List[Dict]`
- `get_todo(id, db_path)` → returns `Optional[Dict]`
- `update_todo(id, title, description, db_path)` → `bool`
- `toggle_todo(id, done=None, db_path)` → `bool` (toggles if `done` is None)
- `delete_todo(id, db_path)` → `bool`

## Templates and UI

- `base.html` provides layout, flash message rendering, and global styles.
- `index.html` shows the add form and the list with actions.
- `edit.html` allows editing title/description.
- Minimal CSS with accessible defaults in `static/style.css`.

## Error handling and UX

- Uses Flask `flash()` to provide success/error messages after redirects.
- If an entity is missing (e.g., edit a non‑existent id), user is redirected to `/` with an error flash.
- Required fields validated on the server (e.g., title not empty).

## Concurrency considerations

- SQLite is file‑based; each helper opens/closes a connection per call, which is safe for this simple app and local usage.
- For higher concurrency, consider: a pooled DB (e.g., Postgres) and a WSGI server (e.g., gunicorn) with proper worker settings.

## Configuration

- `SECRET_KEY`: default `'dev'`; override with `FLASK_SECRET_KEY` env var.
- Database location: `os.path.join(app.instance_path, 'todo.db')` inside the Flask instance folder.

## Testing strategy

- `tests/run_db_tests.py` uses the stdlib (`tempfile`) to validate CRUD functions against a temporary SQLite file.
- Future extensions: add pytest + Flask test client for route tests, and CI to run test suite.

## Deployment notes

- Development server (`app.run(debug=True)`) is not for production.
- For production: use a WSGI server (e.g., `gunicorn 'app:create_app()'`) and a stable database (or ensure file permissions for SQLite).
- Configure `SECRET_KEY` via environment variables; consider CSRF for forms.

## Alternatives to `before_first_request` (Flask ≥ 3.x)

If upgrading to Flask 3.x (where the hook is removed), initialize the DB via one of:
- Call `db.init_db(db_path)` at the end of `create_app()` (eager init).
- Use an application startup event via an extension or appcontext push during startup logic.
- Run a separate init script or a CLI command (e.g., `flask --app app init-db`).

## Security considerations

- Input is server‑validated; template autoescaping protects against basic XSS in fields.
- CSRF protection is not enabled by default; consider `Flask-WTF` or generating a custom CSRF token for forms.
- Authentication/authorization is not implemented; the app is single‑user by design.

## Future enhancements

- Filters (All / Active / Completed), search, pagination
- Due dates, priority, and reminders
- REST/JSON API endpoints for external clients
- ORM (SQLAlchemy) for more complex models
- Dockerfile and CI pipeline
