# AI Software Factory

An integrated engineering platform built in reviewable milestones. Learn architecture through real integrations and failures rather than standalone command exercises.

## Current milestone: application and CI foundation

Implemented: installable FastAPI package with GET /healthz; automated tests; locked dependencies; pull-request quality/security workflow; human ownership of CI configuration. No real agents, task-submission API, repository execution, GitHub application integration, or cloud deployment yet. The original exercises below remain as regression-tested reference material and are not wired into the API.

```text
src/ai_factory/api.py       HTTP application entry point
tests/test_api.py           HTTP contract tests
pyproject.toml              package dependencies and quality configuration
uv.lock                    resolved dependency versions and artifact hashes
.github/workflows/ci.yml    quality, security, and aggregate gate jobs
.github/CODEOWNERS          human ownership of sensitive configuration
```

Install Python 3.11 and uv 0.13.6. A uv installation already exists in this workspace's .venv/Scripts. For this environment, use `.\.venv\Scripts\uv.exe --cache-dir .uv-cache sync --locked --inexact` to preserve that bootstrap tool. With uv installed separately, use `uv sync --locked`.

Run the service from the repository root using `.\.venv\Scripts\python.exe -m uvicorn ai_factory.api:app --host 127.0.0.1 --port 8000`. Open http://127.0.0.1:8000/docs for the API explorer. No environment variables or credentials are needed yet. Health is liveness only, not proof that future workers or storage are available.

CI runs lint/format checks, strict application type checking, all tests (including legacy exercises), package build, Bandit on application source, and an audit of locked runtime/development dependencies. Its ci-gate fails unless both quality and security succeed. Workflow triggers include pull requests, main pushes, manual dispatch, and merge groups. There are no deployment or merge steps, no secret references, and the token has contents:read only.

These files do not enforce repository protection by themselves. After approved publication and a successful remote CI run, require ci-gate on main, require PRs and human review of protected configuration, and restrict bypasses using available repository rules. CODEOWNERS requires corresponding rule enforcement and an eligible reviewer; an author cannot provide the independent approval of their own PR. GitHub feature availability depends on repository visibility and account plan. Merge queue support is prepared but not enabled.

Next integrated milestone: POST /runs and GET /runs/{id}, persisted request records, typed planner/implementer/reviewer contracts, and a provider interface tested with fakes. Then wire one real LLM and a separately authorized synthetic GitHub repository. Parallel agents follow a correct sequential vertical slice, using isolated workspaces.

## Earlier reference exercises

## Run

Requires Python 3.11 or newer. No packages, credentials, environment variables, or cloud account are needed for this lesson. From this directory:

```powershell
python factory.py
python -m unittest -v
```

Expected demo history: received -> implementing -> reviewing -> review_accepted.
Review acceptance is not CI success, merge eligibility, authorization to merge, or release approval.

## Lesson 1: legal state transitions

Concept: a workflow is a set of steps and rules for moving between them. Think of a repair shop: a repaired car must pass inspection before collection.

Why: an LLM suggestion or a misplaced function call must not be enough to skip review. The workflow owner enforces transition rules deterministically.

Architecture: factory.py is the future foreman's domain core. This lesson deliberately omits persistence to isolate one concept.

Walkthrough:
- State gives names to the four stages.
- ALLOWED defines permitted next stages, including a return from review for fixes.
- Task carries a stable identity, current state, and teaching-only history.
- transition checks the rule before creating a new immutable value. It has no external effects.
- main is a scripted driver, not an AI agent or real reviewer.

Experiment: run the demo and tests. Then run this deliberately invalid transition:

```powershell
python -c "from factory import Task, State, transition; transition(Task('experiment'), State.REVIEW_ACCEPTED)"
```

Expect ValueError and a nonzero exit. The exception is the intended outcome.

Checkpoint:
1. Why should transition legality be enforced by code rather than decided by the implementation LLM?
2. If the process exits after entering reviewing, what information does this version lose, and what would you store to resume?

Stop here and discuss your answers before Lesson 2.

Industry comparison: teams use transactional databases or durable workflow engines to enforce and record progress. This in-memory exercise is neither an authorization boundary nor a durable audit trail: callers can construct Task directly, and no reviewer identity or commit evidence is checked yet.

Next: persist task state and event history atomically in SQLite, then inspect them after restarting Python. Add Foreman, fake Implement, and fake Review through replaceable interfaces after that foundation is understood.

See ARCHITECTURE.md, DECISIONS.md, ROADMAP.md, RUNBOOK.md, and LEARNING_LOG.md for the saved design and resume point.

## Lesson 2: persistence and transactions

Think of memory as the foreman's recollection and the database as the written job ledger. Persist both the current state and the record of entering that state. A transaction makes those two writes all-or-nothing, preventing contradictory records after a failed write.

Architecture: lesson2.py (CLI) -> storage.py (SQLite adapter) -> factory.py (transition rules). The adapter also reads/writes a database file; the domain rules do not depend on SQLite.

SQLite needs no database server and ships through Python's sqlite3 module. PostgreSQL is our later shared-worker candidate; it adds server setup and different concurrency behavior. No new packages or environment variables are needed now. `--db` selects a database path; its parent directory must exist. The default is lesson2.db relative to the terminal's current directory.

From this repository directory, run:

```powershell
python lesson2.py create task-001
python lesson2.py move task-001 implementing
python lesson2.py move task-001 reviewing
python lesson2.py show task-001
```

Each command runs in a fresh Python process. The last command should report reviewing with history received, implementing, reviewing. Reopen your terminal in the same directory and repeat show. Repeating create with the same ID raises an error rather than resetting the task; use show to inspect existing work.

Walkthrough of storage.py:
- tasks stores the latest state; events stores ordered entries with UTC timestamps.
- advance starts BEGIN IMMEDIATE before loading current state, reserving the SQLite writer for the short transaction.
- transition applies the same legal-move rules from Lesson 1.
- UPDATE changes current state; INSERT adds its history entry. Question-mark parameters pass values separately from SQL code.
- The connection context commits on successful exit or rolls back on an exception. closing also closes the connection.
- Loading state/history uses one read transaction for a consistent view.

Experiment: after entering reviewing, attempt `python lesson2.py move task-001 received`, then show the task. The invalid move should fail without changing state or history. Run `python -m unittest -v` to exercise a forced history-insert failure after the state update and verify rollback.

Checkpoint: Why must the two writes commit together? If the database says reviewing after restart, does that prove the reviewer completed its work?

Industry comparison: teams use the same transactional principle with shared databases or durable workflow platforms. This adapter provides persistent records, not automatic recovery, reviewer authentication, external-side-effect idempotency, or distributed worker coordination. No LLM call should be held inside this short database transaction.

Next: execution attempts and fake workers, distinguishing a stage being entered from work being completed. Stop for the checkpoint before implementing them.
