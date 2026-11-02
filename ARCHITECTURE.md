# Architecture

Browser HTML/CSS/JavaScript -> same-origin FastAPI JSON API -> SQLite file.

The backend serves both the page and API. There is no frontend build system, separate frontend deployment, cross-origin configuration, agent runtime, or message queue. Browser code uses fetch and renders user text with textContent, never HTML interpolation. Form constraints improve feedback; Pydantic independently validates requests on the server. SQL binds parameters separately from query text.

Each write uses a short transaction. SQLite connections are per operation. Database initialization occurs at application startup. GET lists all tasks; pagination, authentication, multi-user ownership and concurrency version checks are future work, not implied capabilities. Task-status updates use last-write-wins behavior.

CI verifies source and dependencies. No GCP deployment exists. For future Cloud Run use, move task persistence to a managed database rather than an ephemeral container filesystem. A merge and a deployment are separate actions with separate authorization.
