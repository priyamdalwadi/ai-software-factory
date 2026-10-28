# Roadmap and Acceptance Criteria

## Active delivery sequence (supersedes the lesson-by-lesson pacing below)

1. Application + CI foundation: implemented locally; remote CI and required-check enforcement await approved publication/configuration. Acceptance: installable FastAPI service, HTTP tests, lint/format/type checks, package build, static application scan and dependency audit pass; hosted run still required.
2. Integrated run intake: persist a feature request, expose its status, and define agent/provider contracts. Acceptance: request is recoverable, invalid input fails, identities and artifact ownership are explicit.
3. One real feature-to-PR run: planner, implementation, independent review and CI against a separate synthetic application. Acceptance: exact-commit evidence, bounded tools and no automatic merge. Choose provider/account access before paid calls.
4. Parallel workers: isolated branches/workspaces and dependency-aware scheduling. Acceptance: unrelated tasks can run concurrently without overwriting each other's artifacts.
5. GCP staging deployment: incremental approved infrastructure, authentication, shared persistence, queues, secrets and human-controlled releases.
6. Reliability and advanced architecture: durable execution comparison (Workflows/Temporal/Cadence), recovery, observability, cost caps, evaluation and security hardening.

Teach through these deliverables; do not resume standalone beginner exercises unless requested. The concept curriculum below remains reference material.

Advance by demonstrated understanding and passing acceptance checks, not calendar deadlines. Each phase spans multiple small lessons. Lessons 1 and 2 are implemented; Lesson 2 understanding awaits its checkpoint. Phase 2 has begun with persistence; fake workers, attempts, retries, and deduplication are still outstanding.

1. Fundamentals (in progress): architecture, responsibility boundaries, transition rules. Acceptance: demo and negative tests pass; learner explains why review cannot be skipped and predicts memory loss on exit. Stop at that checkpoint.
2. Local minimal orchestrator (planned): SQLite state/events, execution records, deterministic Foreman, fake Implement and Review, bounded review loop. Acceptance: inspect complete history; restart preserves progress; duplicate commands do not repeat completed work; rejected review causes a bounded correction loop.
3. Real agents (planned): compare official provider SDKs; typed outputs, bounded context/tools, isolated synthetic workspaces, independent SHA-bound reviews, limits and failure classes. Acceptance: malformed results and injected instructions cannot expand authority; stale review fails; time/token limits stop runaway work. Mock suite remains credential-free.
4. GitHub (planned, external actions require approval): separate synthetic test repository, GitHub App versus PAT, branch/commit/PR operations, signed webhooks and deduplication. Acceptance: a PR can be created after approval; replay causes no duplicate work; invalid signature rejected; automatic merging disabled.
5. Quality gates (planned): test/lint/security CI, protected workflows, checks at current SHA, immutable review evidence, optional merge queue. Acceptance: stale/missing review, failed CI, protected-file changes, and untrusted evidence all block eligibility; merge_group checks tested if available. Eligibility does not itself authorize merge.
6. GCP (planned, incremental approvals): Docker locally; then one service, shared persistence, IAM/secrets and federated CI auth; then directed delivery and staging. Compare Workflows pilot with current engine. Acceptance: restart/retry survives across instances, no long-lived cloud key in CI, staging artifact traced to approved commit, production waits for human approval. Use infrastructure-as-code when provisioning starts.
7. Reliability (planned): leases, retry backoff, timeouts, outbox, dead letters, replay, tracing, rate/cost caps, rollback. Acceptance: inject crashes before/after side effects and prove no duplicate PR; exercise dead-letter recovery; reject stale worker writes; rehearse rollback and budget enforcement.
8. Advanced factory (planned): optional specialists, dependency graph, parallelism, routing, proposed tickets requiring approval, regression investigation, dashboard. Acceptance: controlled comparison against a single-agent baseline demonstrates benefit without lower quality; reject complexity without measurable value.

## Evaluation plan (not collected yet)

Record task ID, execution/attempt ID, timestamps, role, model/version, prompt version, commit SHA, result, human decisions, token usage, price snapshot, and cost provenance. Keep secrets and raw sensitive prompts out of logs.

- Request-to-PR time: PR creation minus accepted request time; report median/p95 plus incomplete-task count.
- PR acceptance: define acceptance as passing independent review and required CI; denominator all attempted benchmark tasks, including failures. Also report accepted PRs / created PRs to expose selection effects.
- Review rounds: implementation/review cycles per task, including rejected and abandoned runs.
- CI first-pass success: first CI run succeeds / tasks reaching CI; show tasks never reaching CI separately.
- Merge eligibility time: first fully valid evidence set minus intake; exclude no failures silently.
- Human intervention: number, reason, and waiting time; distinguish mandatory approval from repair assistance.
- Tokens and LLM cost: actual usage per attempt, including retries, per successful change and per attempted task; label estimates and missing usage.
- Infrastructure cost: local mock runs have no provider charges; cloud attribution includes shared baseline costs and is approximate when allocation is necessary.
- Agent failure/recovery: failed executions / attempts; recovered failures / retryable failures, classified by cause.
- Regression rate: merged changes causing a confirmed regression within a fixed observation window / merged changes observed for that full window.

Use a fixed synthetic task set with acceptance tests, equal tool/budget constraints, repeated runs, and recorded versions. Report quality alongside throughput and cost. PR count alone is not productivity. Small synthetic samples do not establish performance on real repositories.
