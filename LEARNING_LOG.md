# Learning log

## 2026-11-01 — restart with a full-stack website

User chose to stop factory development, clean the existing repository, and publish a fresh website for learning CI gates and GCP delivery. Preserved all prototype source and unpublished changes on local archive/factory-prototype-2026-11-01 before removing the active files. No Git history was rewritten.

Built Dayboard: plain frontend, FastAPI CRUD endpoints, SQLite persistence, input validation, responsive task board, and fresh CI. No cloud deployment, agents, credentials, or repository rules were added. Verified locally: 11 API/persistence tests, lint, formatting, types, Bandit, dependency audit, package build, and JavaScript syntax passed. Browser checks confirmed task creation, completion/reopening, reload persistence, filtering, and search. Publication uses a normal commit to the existing main branch; GitHub CI verifies the published commit.

Next teaching step: explain the three layers using one create-task request, then demonstrate a page change through a PR and CI. Keep explanations short; do not add features before the learner can locate and understand the app.
