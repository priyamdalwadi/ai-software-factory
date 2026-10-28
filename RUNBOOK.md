# Runbook

## Application and CI checks

The application and dependencies are installed in .venv. From the repository root:

```powershell
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\mypy.exe
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\bandit.exe -r src -ll
.\.venv\Scripts\uv.exe --cache-dir .uv-cache export --locked --no-emit-project --format requirements-txt --output-file audit-requirements.txt --quiet
.\.venv\Scripts\pip-audit.exe --requirement audit-requirements.txt --strict --disable-pip --cache-dir .uv-cache/audit
.\.venv\Scripts\uv.exe --cache-dir .uv-cache build
```

Dependency audit needs advisory-service network access and can fail when that service is unavailable; this must not be treated as a clean audit. It detects known advisories, not all vulnerabilities. Bandit scans application src, not legacy exercises. Mypy likewise targets the new application; pytest includes both.

If HTTP tests hang in the restricted Windows execution environment, faulthandler_timeout=15 can identify event-loop socketpair setup blocking. The same tests passed outside that sandbox. Do not remove tests to work around an environment restriction. Current dependency combination emits a Starlette/httpx deprecation warning; tests pass, but revisit the test client dependency in a future compatibility update.

Before publishing: inspect files and diffs; retain the user's existing staging choices. Initial bootstrap publication requires explicit approval. After remote CI succeeds, separately configure required ci-gate and human workflow-file review, verifying account/repository support. Do not claim protections based solely on workflow/CODEOWNERS files.

## Lesson 2 persisted tasks

Use the Lesson 2 commands in README.md. Run from the repository directory so the default lesson2.db resolves to the same file each time, or supply an absolute `--db` path before the subcommand. Database files are ignored by Git.

`show` loads saved progress; it does not resume worker execution. Duplicate creation raises IntegrityError without resetting the existing task. Illegal transitions raise ValueError without changing the database. An unknown ID raises KeyError. If SQLite reports database locked, check for another process holding a write transaction; do not add blind retries yet.

Nine tests currently cover the domain rules and persistence, including new-process loading and a simulated history-insert failure. This is not a power-loss or forced-process-kill test.

## Current local exercise

From the repository directory, run `python factory.py`, then `python -m unittest -v`.
No installation step or environment variables. Python 3.11+ is required.

Expected failure experiment is in README.md: a direct received -> review_accepted transition raises ValueError. Do not remove the guard to make this experiment succeed.

If imports fail, confirm the terminal is in the directory containing factory.py. If Python is missing from PATH on Windows, try `py -3.11` in place of `python`.

The demo emits one JSON summary correlated by task_id. It is not a durable log. Restarting recreates the example from received; there is currently no crash recovery. No agents or external commands run from the demonstration.

## Future operational procedures

Add only when implemented: database inspection/recovery, webhook replay, lease expiry, dead-letter handling, credential rotation, staging promotion, rollback, cost alerts, and incident simulations.

## External action approval boundary

Before creating billable resources, publishing code, changing external repositories, deploying, or merging, show the exact intended action and obtain user approval. Local work does not grant this authorization. Production releases always need human approval.
