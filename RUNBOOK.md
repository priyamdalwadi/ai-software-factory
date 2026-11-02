# Runbook

Start with the README commands. Default port is 8000. If occupied, choose `--port 8001` and open the matching URL. Stop the development server with Ctrl+C.

Frontend assets and API are served together. A connection error on the page means the API request failed; inspect the server output and /healthz. A 422 response means invalid input; 404 means an unknown task ID; 500 indicates a server/storage failure. Do not treat a failed write as saved.

Database file defaults to dayboard.db in the launching directory. Use an absolute DAYBOARD_DB_PATH when changing launch locations. Stop the server before copying the database for a simple local backup. The file is ignored by Git; pushing source does not upload tasks.

Windows sandbox restrictions can block the event-loop socketpair used by TestClient. Run tests in a normal terminal if they hang there. Do not remove tests to hide environment problems.

CI: quality and security must succeed for ci-gate to succeed. Advisory-service outages can fail auditing and must not be treated as a clean scan. Cloud deployment and enforced repository protections are separate future setup steps.
