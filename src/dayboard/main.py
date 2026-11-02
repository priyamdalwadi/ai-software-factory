"""One same-origin service for the webpage and its JSON API."""

import os
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from dayboard.models import Task, TaskInput, TaskUpdate
from dayboard.storage import TaskStore

STATIC = Path(__file__).parent / "static"


def create_app(database: Path | None = None) -> FastAPI:
    store = TaskStore(database or Path(os.environ.get("DAYBOARD_DB_PATH", "dayboard.db")))

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        store.initialize()
        yield

    application = FastAPI(title="Dayboard API", version="1.0.0", lifespan=lifespan)

    @application.middleware("http")
    async def headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        if request.url.path == "/" or request.url.path.startswith("/static/"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
            )
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @application.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @application.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "dayboard"}

    @application.get("/api/tasks", response_model=list[Task])
    def list_tasks() -> list[Task]:
        return store.list()

    @application.post("/api/tasks", response_model=Task, status_code=201)
    def create_task(request: TaskInput) -> Task:
        return store.create(request)

    @application.patch("/api/tasks/{task_id}", response_model=Task)
    def update_task(task_id: UUID, request: TaskUpdate) -> Task:
        task = store.set_completed(task_id, request.completed)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @application.delete("/api/tasks/{task_id}", status_code=204)
    def delete_task(task_id: UUID) -> Response:
        if not store.delete(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        return Response(status_code=204)

    application.mount("/static", StaticFiles(directory=STATIC), name="static")
    return application


app = create_app()
