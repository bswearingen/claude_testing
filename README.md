## Personal Task Tracker (FastAPI)

This repo contains a small **personal task tracker** web app built with **Python, FastAPI, and SQLite**.

You can:
- **Add** tasks with optional descriptions
- **Mark** tasks as done / not done
- **Delete** tasks
- **Filter** by status (all / active / completed) and **search** by text

The UI is a single-page dashboard with a modern dark theme.

### 1. Setup

From the project root (`claude_testing`):

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows PowerShell
pip install -r requirements.txt
```

### 2. Run the app

From the same directory:

```bash
uvicorn task_tracker.main:app --reload
```

Then open `http://127.0.0.1:8000` in your browser.

On first start, a local SQLite database file `tasks.db` is created in the `task_tracker` folder.

### 3. Project structure

- `requirements.txt` – Python dependencies
- `task_tracker/main.py` – FastAPI app, routes, and SQLite access
- `task_tracker/templates/index.html` – Jinja2 template for the main page
- `task_tracker/static/style.css` – Styling for the dashboard UI

### 4. Next ideas

- Add due dates or priority levels
- Add “clear completed” button
- Add simple tests for the SQLite layer and routes

