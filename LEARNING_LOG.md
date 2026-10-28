# Learning Log

## Publication approval

The user approved committing and pushing the prepared foundation to priyamdalwadi/ai-software-factory and triggering CI. Remote inspection found no existing refs before the initial push. This approval does not authorize GCP deployment or changing repository protection rules. After publication, inspect the hosted quality, security and ci-gate jobs and record their actual results.

## Latest resume point — 2026-10-27, integrated foundation

The user explicitly rejected elementary script-driven lessons and requested building a real integrated multi-agent platform with GitHub CI. Teach architecture while wiring the product. The older checkpoint below is no longer the active stop point.

Implemented locally: src/ai_factory FastAPI health endpoint; two HTTP tests; pyproject.toml/uv.lock; GitHub Actions quality/security jobs and aggregate ci-gate; CODEOWNERS for CI/dependency configuration; Actions Dependabot updates. Preserved earlier exercises and tests, applying Ruff formatting/import fixes and Python 3.11 StrEnum. User's existing staged README was not restaged.

Verification: lint, format, strict application typing, application Bandit scan, package build, and lock consistency pass. pip-audit reported no known vulnerabilities. All 11 tests passed outside the restricted Windows sandbox (plus four unittest subtests); one upstream Starlette/httpx deprecation warning. Restricted test runs hung in event-loop socketpair creation and were terminated. Actions revisions verified against upstream tags. Hosted Linux CI has not run.

No publication, commits, repository rules, real LLM calls, agents, cloud resources, or deployments were performed in this increment. Next action: show the user the concrete publication scope and obtain approval before pushing. Next implementation milestone: integrated run intake, persistence, typed agent contracts, and provider boundaries, not more isolated state-machine exercises.

## Current resume point — 2026-10-27

The learner accepted the distinction between legal transitions and code quality, and the correction that all in-memory state disappears when Python exits. They now authorize local development, report knowing basic Git, and want to move on to architecture and implementation lessons.

Local repository: outputs/software-factory. Branch was renamed main and origin set to https://github.com/priyamdalwadi/ai-software-factory.git. No push was performed by this session. External publishing/deployment still requires the user's prior approval.

Lesson 2 code was written earlier, before an interruption: storage.py, lesson2.py, test_storage.py. Today inspected it, updated documentation, and ran all nine tests successfully. Tests verify reading committed history from a separate Python process, rollback after a forced event-insert failure, invalid-transition rejection, duplicate-create rejection, and missing-task errors, plus the four domain tests. No forced-kill or power-loss test was run.

Teach now: persistence, two-table records, atomic transactions, and the difference between saved state and completed work. Stop at the Lesson 2 checkpoint in README.md. Next milestone is execution attempts with fake workers; do not implement ahead of the learner.

Earlier session notes below are historical, not the current project status.

## Session 1 — 2026-10-25

Goal: establish the architecture and begin Lesson 1, then stop at the first checkpoint.

Introduced (understanding not yet verified): workflow versus agent orchestration; deterministic authority; state transitions; memory versus persistence; evidence versus permission to merge.

Implemented: four-state in-memory task model, legal transition guard, stable task ID, teaching history, JSON demo, and four unittest cases. Required project documentation created. No actual agents, LLM integration, persistence, GitHub integration, cloud infrastructure, or deployments implemented.

Verification: `python factory.py` exited successfully and printed the expected four-state history. `python -m unittest -v` ran four tests, all passing: normal progression, skip-review rejection without mutation, review-to-implementation correction, and no outbound transitions after acceptance. Python 3.11.5 was available. Initialized a local Git repository; no remote, commit, publication, or external changes.

Remaining gaps: learner answers not yet received. Do not mark concepts mastered based solely on reading the lesson.

Resume point: wait for answers to the two README checkpoint questions. Correct misconceptions, then teach atomic SQLite persistence and restart behavior. Do not jump to the full factory.
