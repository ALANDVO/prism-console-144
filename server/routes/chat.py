from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import time
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
    
    # Find the first healthy provider with an enabled API key
    stmt = select(Provider, APIKey).join(APIKey).where(
        Provider.is_enabled == True,
        Provider.health_status == "healthy",
        APIKey.is_enabled == True,
        APIKey.health_status == "healthy"
    ).limit(1)
    
    result = await session.execute(stmt)
    pair = result.one_or_none()
    
    if pair:
        provider, api_key = pair
        response_text = f"Response from {provider.display_name} (model: {request.model}): Mock response to your message"
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
