from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import time
import random
import uuid

from server.database import get_session
from server.models import (
    ChatCompletionRequest, ChatCompletionResponse, 
    ChatCompletionChoice, ChatMessage, ChatCompletionUsage,
    Provider, APIKey
)
from server.services.health_check import health_check_service


router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest, session: AsyncSession = Depends(get_session)):
    """OpenAI-compatible chat completions endpoint with provider routing."""
    # Check if tables exist first
    try:
        await session.execute(text("SELECT 1 FROM providers LIMIT 1"))
    except Exception:
        # Tables don't exist yet, return mock response
        response_text = f"Mock response to: {request.messages[-1].content if request.messages else 'empty'} (Database not initialized)"
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:29]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=response_text
                    ),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=len(str(request.messages)),
                completion_tokens=len(response_text) // 4,
                total_tokens=len(str(request.messages)) + len(response_text) // 4
            )
        )
    
    # Find healthy providers with enabled API keys
    # Select based on provider routing_strategy if set
    stmt = select(Provider, APIKey).join(APIKey).where(
        Provider.is_enabled == True,
        Provider.health_status == "healthy",
        APIKey.is_enabled == True,
        APIKey.health_status == "healthy"
    )
    
    result = await session.execute(stmt)
    providers_keys = result.all()
    
    # Apply routing strategy selection
    selected_provider = None
    selected_api_key = None
    
    if providers_keys:
        # Determine routing strategy from provider (first one that sets it)
        strategy: Optional[str] = None
        for prov, key in providers_keys:
            if prov.routing_strategy in ("round_robin", "random", "priority"):
                strategy = prov.routing_strategy
                break

        # Apply the selected strategy
        if strategy == "round_robin":
            # Select first available; index tracking can be added per-session later
            selected_provider, selected_api_key = providers_keys[0]
        elif strategy == "random":
            selected_provider, selected_api_key = random.choice(providers_keys)
        elif strategy == "priority":
            # Prefer providers with priority strategy; fall back to first available
            priority_entries = [(p, k) for p, k in providers_keys if p.routing_strategy == "priority"]
            if priority_entries:
                selected_provider, selected_api_key = priority_entries[0]
            else:
                selected_provider, selected_api_key = providers_keys[0]
        else:
            # No strategy set; default to first available
            selected_provider, selected_api_key = providers_keys[0]
    
    if selected_provider and selected_api_key:
        response_text = f"Response from {selected_provider.display_name} (model: {request.model}): Mock response to your message"
    else:
        response_text = f"Mock response to: {request.messages[-1].content if request.messages else 'empty'} (No healthy providers configured)"
    
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:29]}",
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content=response_text
                ),
                finish_reason="stop"
            )
        ],
        usage=ChatCompletionUsage(
            prompt_tokens=len(str(request.messages)),
            completion_tokens=len(response_text) // 4,
            total_tokens=len(str(request.messages)) + len(response_text) // 4
        )
    )
