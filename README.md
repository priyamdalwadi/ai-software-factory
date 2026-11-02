# Dayboard

A small full-stack task board, built from scratch to learn GitHub CI, review gates, and GCP delivery. The repository keeps its existing name `ai-software-factory`; its active application is now Dayboard. The old agent-factory prototype is preserved locally on `archive/factory-prototype-2026-11-01`.

## What works

- Create tasks with a title, optional notes, and a priority.
- Mark tasks complete or reopen them; filter and search the board.
- Delete tasks after confirmation.
- Persist changes in SQLite across server restarts.
- Responsive, keyboard-accessible frontend with loading/error/empty states.

## Project map

```text
src/dayboard/
  main.py              website and API routes
  models.py            request validation
  storage.py           database operations
  static/
    index.html         webpage structure
    style.css          responsive design
    app.js             browser interactions and API calls
tests/test_app.py      automated backend and persistence checks
.github/workflows/ci.yml  GitHub checks
```

## Run locally

Requires Python 3.11–3.13 and uv 0.13.6. With uv installed separately:

```powershell
uv sync --locked
uv run --locked uvicorn dayboard.main:app --host 127.0.0.1 --port 8000
```

In the existing Windows workspace uv is inside .venv. Preserve that bootstrap tool with:

```powershell
.\.venv\Scripts\uv.exe --cache-dir .uv-cache sync --locked --inexact
.\.venv\Scripts\python.exe -m uvicorn dayboard.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the website or /docs for the API explorer. Optional `DAYBOARD_DB_PATH` selects the SQLite file; default `dayboard.db` is relative to the working directory, and its parent must exist. No credentials, cloud account, or API key is required.

## API

- `GET /healthz`: service liveness.
- `GET /api/tasks`: list tasks, newest first.
- `POST /api/tasks`: create using title, notes, priority; returns 201.
- `PATCH /api/tasks/{id}`: set completed to a Boolean.
- `DELETE /api/tasks/{id}`: delete; returns 204.

## Verification and CI

Run `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run bandit -r src -ll`, and `uv build`. CI also checks JavaScript syntax and audits locked dependencies for known vulnerabilities. Quality and security jobs feed ci-gate. No deployment occurs in CI. Repository rules must separately require passing checks; CODEOWNERS alone does not enforce human approval.

## Scope

This is a single-workspace learning app without authentication. Bind to localhost and use non-sensitive example tasks. It is not ready for public multi-user use. SQLite on a Cloud Run instance's local filesystem would not provide durable shared storage; choose managed persistence and access controls before cloud deployment. No cloud resources have been created.

Next lesson: a small page change on a branch -> PR -> CI failure/fix -> required gates -> authorized merge. GCP identity, containers, staging, and production approval follow later.
