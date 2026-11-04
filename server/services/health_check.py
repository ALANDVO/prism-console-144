import asyncio
import hashlib
import json
import time
from datetime import datetime
from typing import Optional, List
import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import async_session_maker
from server.models import Provider, APIKey, HealthStatus, HealthCheckResponse
from server.config import settings


class HealthCheckService:
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.health_check_timeout_seconds),
                follow_redirects=True
            )
        return self._client
    
    async def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(settings.health_check_concurrency)
        return self._semaphore
    
    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _get_key_prefix(self, key: str) -> str:
        return key[:8] + "..." + key[-4:] if len(key) > 12 else key[:4] + "..." + key[-4:]
    
    async def check_provider(self, provider: Provider) -> HealthCheckResponse:
        """Check a single provider's /models endpoint."""
        start_time = time.time()
        url = str(provider.base_url).rstrip("/") + provider.models_endpoint
        
        try:
            client = await self._get_client()
            semaphore = await self._get_semaphore()
            
            async with semaphore:
                response = await client.get(url)
                latency_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    data = response.json()
                    models_count = len(data.get("data", [])) if isinstance(data, dict) else 0
                    
                    return HealthCheckResponse(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        status=HealthStatus.HEALTHY,
                        checked_at=datetime.utcnow(),
                        models_count=models_count,
                        latency_ms=latency_ms
                    )
                else:
                    return HealthCheckResponse(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        status=HealthStatus.UNHEALTHY,
                        checked_at=datetime.utcnow(),
                        error=f"HTTP {response.status_code}: {response.text[:200]}",
                        latency_ms=latency_ms
                    )
        except httpx.TimeoutException:
            return HealthCheckResponse(
                provider_id=provider.id,
                provider_name=provider.name,
                status=HealthStatus.UNHEALTHY,
                checked_at=datetime.utcnow(),
                error="Request timeout",
                latency_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return HealthCheckResponse(
                provider_id=provider.id,
                provider_name=provider.name,
                status=HealthStatus.UNHEALTHY,
                checked_at=datetime.utcnow(),
                error=str(e)[:200],
                latency_ms=int((time.time() - start_time) * 1000)
            )
    
    async def check_api_key(self, api_key: APIKey, provider: Provider) -> HealthCheckResponse:
        """Check a specific API key by calling /models with auth."""
        start_time = time.time()
        url = str(provider.base_url).rstrip("/") + provider.models_endpoint
        
        try:
            client = await self._get_client()
            semaphore = await self._get_semaphore()
            
            headers = {"Authorization": f"Bearer {api_key.key_hash}"}
            
            async with semaphore:
                response = await client.get(url, headers=headers)
                latency_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    data = response.json()
                    models_count = len(data.get("data", [])) if isinstance(data, dict) else 0
                    models_json = json.dumps(data.get("data", []))
                    
                    return HealthCheckResponse(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        status=HealthStatus.HEALTHY,
                        checked_at=datetime.utcnow(),
                        models_count=models_count,
                        latency_ms=latency_ms
                    )
                elif response.status_code == 401:
                    return HealthCheckResponse(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        status=HealthStatus.UNHEALTHY,
                        checked_at=datetime.utcnow(),
                        error="Invalid API key (401)",
                        latency_ms=latency_ms
                    )
                elif response.status_code == 429:
                    return HealthCheckResponse(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        status=HealthStatus.DEGRADED,
                        checked_at=datetime.utcnow(),
                        error="Rate limited (429)",
                        latency_ms=latency_ms
                    )
                else:
                    return HealthCheckResponse(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        status=HealthStatus.UNHEALTHY,
                        checked_at=datetime.utcnow(),
                        error=f"HTTP {response.status_code}: {response.text[:200]}",
                        latency_ms=latency_ms
                    )
        except httpx.TimeoutException:
            return HealthCheckResponse(
                provider_id=provider.id,
                provider_name=provider.name,
                status=HealthStatus.UNHEALTHY,
                checked_at=datetime.utcnow(),
                error="Request timeout",
                latency_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return HealthCheckResponse(
                provider_id=provider.id,
                provider_name=provider.name,
                status=HealthStatus.UNHEALTHY,
                checked_at=datetime.utcnow(),
                error=str(e)[:200],
                latency_ms=int((time.time() - start_time) * 1000)
            )
    
    async def update_provider_health(self, provider_id: int, result: HealthCheckResponse):
        """Update provider health status in database."""
        async with async_session_maker() as session:
            stmt = (
                update(Provider)
                .where(Provider.id == provider_id)
                .values(
                    health_status=result.status,
                    last_health_check=result.checked_at,
                    last_health_error=result.error if result.status != HealthStatus.HEALTHY else None,
                    updated_at=datetime.utcnow()
                )
            )
            await session.execute(stmt)
            await session.commit()
    
    async def update_api_key_health(self, api_key_id: int, result: HealthCheckResponse, models_cache: Optional[str] = None):
        """Update API key health status in database."""
        async with async_session_maker() as session:
            values = {
                "health_status": result.status,
                "last_health_check": result.checked_at,
                "last_health_error": result.error if result.status != HealthStatus.HEALTHY else None,
                "updated_at": datetime.utcnow()
            }
            if models_cache is not None:
                values["models_cache"] = models_cache
            
            stmt = update(APIKey).where(APIKey.id == api_key_id).values(**values)
            await session.execute(stmt)
            await session.commit()
    
    async def run_provider_health_checks(self):
        """Run health checks for all enabled providers."""
        async with async_session_maker() as session:
            stmt = select(Provider).where(Provider.is_enabled == True)
            result = await session.execute(stmt)
            providers = result.scalars().all()
        
        if not providers:
            return
        
        tasks = [self.check_provider(p) for p in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                error_result = HealthCheckResponse(
                    provider_id=provider.id,
                    provider_name=provider.name,
                    status=HealthStatus.UNHEALTHY,
                    checked_at=datetime.utcnow(),
                    error=str(result)[:200]
                )
                await self.update_provider_health(provider.id, error_result)
            else:
                await self.update_provider_health(provider.id, result)
    
    async def run_api_key_health_checks(self):
        """Run health checks for all enabled API keys."""
        async with async_session_maker() as session:
            stmt = select(APIKey, Provider).join(Provider).where(
                APIKey.is_enabled == True,
                Provider.is_enabled == True
            )
            result = await session.execute(stmt)
            pairs = result.all()
        
        if not pairs:
            return
        
        async def check_pair(api_key: APIKey, provider: Provider):
            result = await self.check_api_key(api_key, provider)
            await self.update_api_key_health(api_key.id, result)
        
        tasks = [check_pair(ak, p) for ak, p in pairs]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def run_all_health_checks(self):
        """Run all health checks."""
        await self.run_provider_health_checks()
        await self.run_api_key_health_checks()
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


health_check_service = HealthCheckService()
