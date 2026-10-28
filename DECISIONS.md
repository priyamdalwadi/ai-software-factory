# Architectural Decisions

## ADR 005: Integrated product milestones and CI baseline

Status: implemented locally, publication awaiting approval.

Compare continuing isolated command exercises with a deployable application package and integration milestones. The user chose the latter. Preserve existing examples/tests, introduce src/ai_factory, and explain architecture at integration boundaries. FastAPI versus a lower-level ASGI application: choose FastAPI for typed HTTP contracts and API documentation. This first package exposes liveness only.

Dependency management: pip requirements files versus uv project locking. Select pyproject.toml + uv.lock for one cross-platform resolved dependency graph and locked CI installs. Pin the bootstrap uv version; uv.lock records package hashes. Build backend dependencies are separately constrained by build-system requirements, not fully covered by the runtime/development lock audit.

CI: one monolithic job versus independent quality/security jobs. Select two jobs and a stable aggregate ci-gate. Require both success results, so a skipped/cancelled/failed prerequisite cannot make the aggregate gate green. The aggregate is a convenience, not an independent trust boundary: protected workflow ownership and server-side rules remain necessary. A PR can otherwise modify its own checks.

Actions are pinned to verified commit SHAs; checkout does not persist credentials. Use pull_request rather than pull_request_target for untrusted code. CI needs no cloud or LLM credentials. Publication, repository rules, secret scanning availability, CodeQL, provenance, container scans, SHA-bound independent review, and deployment approval controls remain future work, not claimed as enabled.

Sources: https://docs.astral.sh/uv/guides/integration/github/ ; https://fastapi.tiangolo.com/tutorial/testing/ ; https://docs.github.com/en/actions/reference/security/secure-use ; https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

## Lesson 2 implementation note

Implemented ADR 002 with Python sqlite3, separate tasks/events tables, and a short transaction for each transition. Compared independent writes (simpler but can disagree on failure) with one transaction; selected the transaction. BEGIN IMMEDIATE reserves the writer before reading current state. This serializes local writes; distributed leases and stale-worker protection remain future work. No external work occurs inside the transaction.

## ADR 001: Start with application-level orchestration

Status: selected for the local learning baseline; reconsider at the reliability milestone.

Options:
1. Python state machine + SQLite: no services to operate, easy to inspect and test. We must implement transactions, leases, retries, idempotency, and reconciliation ourselves. Appropriate for learning and a small local baseline, not a claim of production readiness.
2. GCP Workflows: managed orchestration of HTTP services and Google Cloud connectors, with explicit execution order. Good fit for later GCP release coordination; cloud setup and a workflow definition language add friction to the first free local exercise.
3. Temporal: durable code-based workflows backed by execution history. Strong fit for long waits and complex recovery; requires a Temporal service and learning replay/determinism rules. External side effects still require retry-safe activity design.

Decision: teach the small core first, then evaluate whether owning its reliability code remains worthwhile. No full workflow platform recreation as a project goal.

Sources checked for the initial design:
- https://docs.cloud.google.com/workflows/docs/overview
- https://docs.temporal.io/workflows
- https://docs.temporal.io/encyclopedia/event-history

## ADR 002: SQLite first, PostgreSQL before distributed workers

SQLite versus PostgreSQL: SQLite needs no separate server and supports local transactions. PostgreSQL adds operational setup but better fits shared concurrent workers and relational evidence. Firestore is a viable managed alternative; relational task/execution/review relationships favor PostgreSQL for this curriculum. Migrations and concurrency semantics must be tested, not assumed identical.

Lesson 1 uses in-memory values solely as a teaching increment. Persistence begins in the next lesson. Use Python's built-in sqlite3 for that increment; postpone third-party SDK selection until its lesson, consulting official docs at that time.

Source: https://docs.python.org/3.11/library/sqlite3.html

## ADR 003: Deterministic foreman, replaceable workers

Compare a free-form LLM manager with a typed state machine. Select the state machine for authority over progression, retry limits, and approvals. An LLM may recommend routing but cannot override policy. Use plain Python interfaces initially rather than adopting an agent framework before tool and recovery requirements are known.

## ADR 004: Add messaging only for a demonstrated need

Direct calls suffice for the first process. A database-backed work queue teaches persistence and recovery. Introduce Cloud Tasks for directed, scheduled/rate-controlled delivery; use Pub/Sub when multiple independent consumers need events. Neither replaces authoritative task state or consumer deduplication.

Sources:
- https://docs.cloud.google.com/pubsub/docs/choosing-pubsub-or-cloud-tasks
- https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run

GitHub merge queues are optional and account/repository dependent. Verify availability at Phase 5. Queue CI needs merge_group coverage; testing a PR head alone is insufficient for the queued integration candidate.
Source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
