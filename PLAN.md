# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

implement-provider-health-checks

## Roadmap

### implement-provider-health-checks — Provider health check system with /models endpoint validation

Status: done

Acceptance:
- Add Provider and APIKey models with database persistence
- Implement health check endpoint that validates provider /models endpoint
- Add background health check scheduler
- Expose health status via API
- Tests pass for health check functionality

Implementation: `server/models.py`, `server/database.py`, `server/config.py`, `server/services/health_check.py`, `server/services/scheduler.py`, `server/routes/providers.py`, `server/routes/chat.py`

Tests: `tests/test_chat_endpoint.py`

### implement-routing-engine — Smart routing with fallback and load balancing

Status: planned

Acceptance:
- Implement routing strategy selection
- Add fallback chain logic
- Track per-model/per-key latency and error rates
- Integration tests for routing decisions

### implement-streaming-support — Server-sent events streaming for chat completions

Status: planned

Acceptance:
- Add stream=true support to chat completions
- Implement SSE response format
- Handle cancellation and timeouts properly

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
