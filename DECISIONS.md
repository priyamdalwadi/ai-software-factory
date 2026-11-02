# Decisions

## Fresh website instead of agent factory

The learner requested replacing all active prototype files with a small full-stack website while retaining the same GitHub repository. Old source and unpublished work were committed to a local archive branch before cleanup; Git history is retained, not force-rewritten.

## Simple frontend + FastAPI

Compared React plus a separate backend with plain HTML/CSS/JavaScript served by FastAPI. Chose one service because the learning priority is the delivery pipeline rather than frontend tooling. It is genuinely full-stack: user interactions call a Python API that persists records. Future frontend complexity can justify a framework.

## SQLite for the first milestone

Compared a serverless managed database with a local SQLite file. SQLite needs no account or billing and makes persistence observable today. It is only a single-host teaching choice; shared cloud storage must replace it before durable Cloud Run deployment.

## CI retained as newly written configuration

Quality (lint, format, types, tests, JS syntax, package build) and security (Bandit, known dependency advisories) run independently. A final ci-gate requires both to succeed. Actions are pinned to verified v6 revisions and runners to Ubuntu 24.04. Runtime deployment and branch rules are deliberately not configured by this change.
