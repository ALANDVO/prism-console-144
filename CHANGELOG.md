# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added
- Provider and APIKey database models with SQLAlchemy + aiosqlite
- Health check service with concurrent /models endpoint validation
- Background health check scheduler (APScheduler)
- Provider management API (CRUD + health check triggers)
- Chat completions endpoint with provider routing
- Configuration management with Pydantic Settings

### Changed
- Chat completions now routes to healthy providers when available
- Database auto-initialization on startup via FastAPI lifespan

### Infrastructure
- Added sqlalchemy, aiosqlite, apscheduler dependencies
- Test infrastructure with pytest-asyncio and httpx
