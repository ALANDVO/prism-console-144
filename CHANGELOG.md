# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added
- `.env.example` file with all configuration options documented

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Fixed
- **Critical bug fix**: API key health checks now work correctly. Changed API key storage from one-way SHA256 hashing to reversible Fernet encryption, allowing health checks to decrypt and authenticate with the actual API key.
- Added `server/services/encryption.py` with Fernet-based encryption/decryption service.
- Added `encryption_key` configuration setting (requires `ENCRYPTION_KEY` environment variable).
- Added `cryptography` dependency.

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

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
