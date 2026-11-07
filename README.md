# prism-console-144 — Alan Vo

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python -m server.main

# Or with uvicorn directly
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

Server runs at http://localhost:8000

## API Endpoints

### Health
- `GET /health` - Service health check

### Chat Completions (OpenAI-compatible)
- `POST /v1/chat/completions` - Chat completion endpoint

### Provider Management
- `POST /v1/providers` - Create provider
- `GET /v1/providers` - List providers
- `GET /v1/providers/{id}` - Get provider
- `PATCH /v1/providers/{id}` - Update provider
- `DELETE /v1/providers/{id}` - Delete provider

### API Key Management
- `POST /v1/providers/{provider_id}/keys` - Add API key
- `GET /v1/providers/{provider_id}/keys` - List API keys
- `GET /v1/providers/{provider_id}/keys/{key_id}` - Get API key
- `PATCH /v1/providers/{provider_id}/keys/{key_id}` - Update API key
- `DELETE /v1/providers/{provider_id}/keys/{key_id}` - Delete API key

### Health Checks
- `POST /v1/providers/{id}/health-check` - Trigger provider health check
- `POST /v1/providers/{pid}/keys/{kid}/health-check` - Trigger API key health check
- `POST /v1/providers/health-check/all` - Trigger all health checks

## Configuration

Environment variables (`.env` file):
```
DATABASE_URL=sqlite+aiosqlite:///./prism.db
HEALTH_CHECK_INTERVAL_SECONDS=300
HEALTH_CHECK_TIMEOUT_SECONDS=10
HEALTH_CHECK_CONCURRENCY=5
HOST=0.0.0.0
PORT=8000
```

## Testing

```bash
pytest tests/ -v
```

## Architecture

- **FastAPI** - Web framework
- **SQLAlchemy 2.0 + aiosqlite** - Async database
- **APScheduler** - Background job scheduling
- **httpx** - Async HTTP client for health checks
- **Pydantic Settings** - Configuration management

Maintainer: Alan Vo <alanvo@gmail.com>

---

Alan Vo · [alanvo.net](https://alanvo.net)
