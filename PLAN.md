# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

implement-routing-engine

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

Status: in_progress

Acceptance:
- Implement routing strategy selection with round_robin/random/priority support
- Add fallback chain logic
- Track per-model/per-key latency and error rates
- Integration tests for routing decisions

Implementation: `server/models.py - routing_strategy column on Provider and APIKey`, `server/routes/chat.py - routing strategy selection in chat completions`, `server/routes/providers.py - routing_strategy CRUD endpoints`

Tests: `tests/test_routing_strategy.py - new test file for routing strategy`

### implement-streaming-support — Server-sent events streaming for chat completions

Status: planned

Acceptance:
- Add stream=true support to chat completions
- Implement SSE response format
- Handle cancellation and timeouts properly

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
