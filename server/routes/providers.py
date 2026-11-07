from fastapi import APIRouter, HTTPException, Depends, status
from server.services.encryption import encryption_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from server.database import get_session
from server.models import (
    Provider, APIKey, ProviderCreate, ProviderUpdate, ProviderResponse,
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, HealthStatus
)
from server.services.health_check import health_check_service


router = APIRouter(prefix="/v1/providers", tags=["providers"])


# Provider CRUD
@router.post("", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(provider: ProviderCreate, session: AsyncSession = Depends(get_session)):
    """Create a new provider."""
    # Check if name already exists
    stmt = select(Provider).where(Provider.name == provider.name)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Provider with this name already exists")
    
    db_provider = Provider(
        name=provider.name,
        display_name=provider.display_name,
        type=provider.type,
        base_url=str(provider.base_url),
        models_endpoint=provider.models_endpoint,
        is_enabled=provider.is_enabled
    )
    session.add(db_provider)
    await session.commit()
    await session.refresh(db_provider)
    return db_provider


@router.get("", response_model=List[ProviderResponse])
async def list_providers(session: AsyncSession = Depends(get_session)):
    """List all providers."""
    stmt = select(Provider).order_by(Provider.id)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific provider."""
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await session.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: int, 
    provider_update: ProviderUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Update a provider."""
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await session.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    update_data = provider_update.model_dump(exclude_unset=True)
    if "base_url" in update_data:
        update_data["base_url"] = str(update_data["base_url"])
    
    for field, value in update_data.items():
        setattr(provider, field, value)
    
    provider.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(provider)
    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a provider."""
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await session.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    await session.delete(provider)
    await session.commit()


# API Key CRUD
@router.post("/{provider_id}/keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    provider_id: int, 
    key_data: APIKeyCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Add an API key to a provider."""
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await session.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    # Encrypt the key for storage
    key_encrypted = encryption_service.encrypt(key_data.api_key)
    key_prefix = key_data.api_key[:8] + "..." + key_data.api_key[-4:] if len(key_data.api_key) > 12 else key_data.api_key[:4] + "..." + key_data.api_key[-4:]
    
    db_key = APIKey(
        provider_id=provider_id,
        name=key_data.name,
        key_encrypted=key_encrypted,
        key_prefix=key_prefix
    )
    session.add(db_key)
    await session.commit()
    await session.refresh(db_key)
    return db_key


@router.get("/{provider_id}/keys", response_model=List[APIKeyResponse])
async def list_api_keys(provider_id: int, session: AsyncSession = Depends(get_session)):
    """List all API keys for a provider."""
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await session.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    stmt = select(APIKey).where(APIKey.provider_id == provider_id).order_by(APIKey.id)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{provider_id}/keys/{key_id}", response_model=APIKeyResponse)
async def get_api_key(provider_id: int, key_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific API key."""
    stmt = select(APIKey).where(APIKey.id == key_id, APIKey.provider_id == provider_id)
    result = await session.execute(stmt)
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@router.patch("/{provider_id}/keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    provider_id: int,
    key_id: int,
    key_update: APIKeyUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an API key."""
    stmt = select(APIKey).where(APIKey.id == key_id, APIKey.provider_id == provider_id)
    result = await session.execute(stmt)
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    update_data = key_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(api_key, field, value)
    
    api_key.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(api_key)
    return api_key


@router.delete("/{provider_id}/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(provider_id: int, key_id: int, session: AsyncSession = Depends(get_session)):
    """Delete an API key."""
    stmt = select(APIKey).where(APIKey.id == key_id, APIKey.provider_id == provider_id)
    result = await session.execute(stmt)
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    await session.delete(api_key)
    await session.commit()


# Health check endpoints
@router.post("/{provider_id}/health-check", response_model=dict)
async def trigger_provider_health_check(provider_id: int, session: AsyncSession = Depends(get_session)):
    """Manually trigger a health check for a provider."""
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await session.execute(stmt)
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    result = await health_check_service.check_provider(provider)
    await health_check_service.update_provider_health(provider.id, result)
    
    return {
        "provider_id": provider.id,
        "provider_name": provider.name,
        "status": result.status.value,
        "checked_at": result.checked_at.isoformat(),
        "error": result.error,
        "models_count": result.models_count,
        "latency_ms": result.latency_ms
    }


@router.post("/{provider_id}/keys/{key_id}/health-check", response_model=dict)
async def trigger_api_key_health_check(provider_id: int, key_id: int, session: AsyncSession = Depends(get_session)):
    """Manually trigger a health check for an API key."""
    stmt = select(APIKey, Provider).join(Provider).where(
        APIKey.id == key_id,
        APIKey.provider_id == provider_id
    )
    result = await session.execute(stmt)
    pair = result.one_or_none()
    if not pair:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key, provider = pair
    result = await health_check_service.check_api_key(api_key, provider)
    await health_check_service.update_api_key_health(api_key.id, result)
    
    return {
        "api_key_id": api_key.id,
        "api_key_name": api_key.name,
        "provider_name": provider.name,
        "status": result.status.value,
        "checked_at": result.checked_at.isoformat(),
        "error": result.error,
        "models_count": result.models_count,
        "latency_ms": result.latency_ms
    }


@router.post("/health-check/all", response_model=dict)
async def trigger_all_health_checks():
    """Manually trigger health checks for all providers and keys."""
    await health_check_service.run_all_health_checks()
    return {"message": "Health checks triggered for all providers and API keys"}
