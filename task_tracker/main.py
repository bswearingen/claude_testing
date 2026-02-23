from pathlib import Path
import sqlite3
from typing import List, Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                is_done INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


app = FastAPI(title="Personal Task Tracker")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup_event() -> None:
    init_db()


def fetch_tasks(search: Optional[str] = None, status: Optional[str] = None) -> List[sqlite3.Row]:
    query = "SELECT * FROM tasks"
    params: list = []

    filters = []
    if search:
        filters.append("(title LIKE ? OR description LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like])

    if status == "active":
        filters.append("is_done = 0")
    elif status == "completed":
        filters.append("is_done = 1")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY created_at DESC"

    with get_connection() as conn:
        cur = conn.execute(query, params)
        return cur.fetchall()


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    search: Optional[str] = None,
    status: Optional[str] = None,
) -> HTMLResponse:
    tasks = fetch_tasks(search=search, status=status)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tasks": tasks,
            "search": search or "",
            "status": status or "all",
        },
    )


@app.post("/tasks")
async def create_task(
    title: str = Form(...),
    description: str = Form(""),
) -> RedirectResponse:
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title.strip(), description.strip() or None),
        )
        conn.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/toggle")
async def toggle_task(task_id: int) -> RedirectResponse:
    with get_connection() as conn:
        cur = conn.execute("SELECT is_done FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        new_value = 0 if row["is_done"] else 1
        conn.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (new_value, task_id))
        conn.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/delete")
async def delete_task(task_id: int) -> RedirectResponse:
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

    return RedirectResponse(url="/", status_code=303)

