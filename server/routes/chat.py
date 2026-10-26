from fastapi import APIRouter, HTTPException
from server.models import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice, ChatMessage, ChatCompletionUsage
import time
import uuid

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    # Mock response for now - returns a simple echo
    response_text = f"Mock response to: {request.messages[-1].content if request.messages else 'empty'}"
    
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
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    )
