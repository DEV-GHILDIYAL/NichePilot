# Environments and configuration

**Development:** Phase 1 runs FastAPI locally with PostgreSQL in Docker Compose. There is no worker or external provider. **Test:** use a separate PostgreSQL database ending in `_test`, no live credentials. **Production:** single-host Docker Compose on an existing EC2 instance remains a future plan; Phase 1 is not a production deployment.

## Phase 1 local commands

From the repository root, copy [`.env.example`](../../.env.example) to untracked `.env`. Set `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `TEST_DATABASE_URL`, and a strong `ADMIN_API_TOKEN`. The URL format is `postgresql+psycopg://USER:PASSWORD@127.0.0.1:5432/nichepilot`; the test URL must end in `nichepilot_test`. Keep both databases local and use different database names. No value belongs in Git.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e 'backend[dev]'
docker compose up -d db
docker compose exec db sh -c 'createdb -U "$POSTGRES_USER" nichepilot_test'
.venv\Scripts\alembic -c backend/alembic.ini upgrade head
.venv\Scripts\uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In a second terminal, run the checks below. Pydantic Settings reads `.env` for the backend, migration, and tests; Docker Compose reads it for PostgreSQL.

```powershell
.venv\Scripts\python -m pytest backend/tests
.venv\Scripts\ruff check backend
.venv\Scripts\ruff format --check backend
.venv\Scripts\mypy backend/app
```

The API has `GET /health/live` and `GET /health/ready`; account routes require `Authorization: Bearer <ADMIN_API_TOKEN>`. Do not place this token in browser code. The account API and event cursor contract are in [domain model](../architecture/domain-model.md).

To exercise the authorized API from another PowerShell terminal, set `$env:ADMIN_API_TOKEN` to the same local token, then run:

```powershell
$headers = @{ Authorization = "Bearer $env:ADMIN_API_TOKEN" }
Invoke-RestMethod http://127.0.0.1:8000/api/v1/accounts -Headers $headers
```

Create an account with `POST /api/v1/accounts` using an initial `niche_dna` object, then use the returned ID for `GET /api/v1/accounts/{id}/niche-dna` and `GET /api/v1/accounts/{id}/events`. The request fields are published in the FastAPI OpenAPI schema at `/openapi.json`; the [backend module guide](../../backend/README.md) summarizes the write contracts.

Real credentials go in untracked environment configuration. A secret manager can replace that source later. Startup rejects missing database URL, missing administrator token outside tests, or live automation/publishing settings. Never print secrets in errors or logs.

Keep free-first operation visible through provider usage, quota, and estimated cost records when providers exist. Define backup and restore, retention, and deployment commands before production. See [observability](../architecture/observability.md) and [security controls](../architecture/security-and-controls.md).
