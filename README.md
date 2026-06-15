# Surfaced

Job board aggregating tech positions in Kazakhstan from HeadHunter.kz and Telegram channels.

## Stack

**Backend:** FastAPI · PostgreSQL (full-text search) · Redis · Celery · SQLAlchemy  
**Frontend:** Next.js 15 · TypeScript · Tailwind CSS  
**Infrastructure:** Docker · GitHub Actions

## Local development

### Prerequisites
- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- Docker (for Postgres + Redis)

### Backend

```bash
docker compose up db redis -d
uv sync
cp .env.example .env        # fill in values
uv run alembic upgrade head
PYTHONPATH=src uv run uvicorn surfaced.main:app --reload
```

API at `http://localhost:8000` · Swagger at `http://localhost:8000/docs`

### Celery workers

```bash
PYTHONPATH=src uv run celery -A surfaced.worker.celery_app worker --loglevel=info
PYTHONPATH=src uv run celery -A surfaced.worker.celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Frontend at `http://localhost:3000`

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | JWT key — `openssl rand -hex 32` |
| `POSTGRES_*` | ✅ | Database connection |
| `REDIS_URL` | ✅ | Redis URL |
| `CORS_ORIGINS` | ⬜ | Comma-separated allowed frontend origins |
| `SENTRY_DSN` | ⬜ | Error tracking (leave empty to disable) |
| `HH_APPLICATION_TOKEN` | ⬜ | HeadHunter.kz API token |
| `TELEGRAM_API_ID` | ⬜ | From my.telegram.org |
| `TELEGRAM_API_HASH` | ⬜ | From my.telegram.org |
| `TELEGRAM_SESSION_STRING` | ⬜ | Generated via `scripts/generate_telegram_session.py` |

## Telegram one-time setup

```bash
uv run python scripts/generate_telegram_session.py
# paste the printed TELEGRAM_SESSION_STRING into .env
```

## Scraping schedule

| Task | Schedule | Source |
|---|---|---|
| `scrape_and_load_hh_vacancies` | Daily midnight | HeadHunter.kz |
| `enrich_hh_vacancies` | Every 30 min | HeadHunter.kz (fills descriptions) |
| `scrape_telegram_channels` | Every 6 hours | @devkz_jobs · @workitkz |

## Production deployment

```bash
cp .env.example .env    # fill with production values
docker compose up -d
docker compose logs -f app
```

`docker compose up` starts: `app` (FastAPI on :8000), `worker`, `beat`, `db`, `redis`.  
Migrations run automatically on container start.

## API

```
GET  /health
GET  /api/v1/jobs               ?q= &location= &source= &limit= &cursor=
GET  /api/v1/jobs/{id}
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/token/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
PATCH /api/v1/auth/me
PATCH /api/v1/auth/password
GET  /api/v1/jobs/me/saved
POST /api/v1/jobs/me/saved
DELETE /api/v1/jobs/me/saved/{id}
```
