from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from server.database import Base
import uuid


class HealthStatus(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class ProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    CUSTOM = "custom"


class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    type = Column(SQLEnum(ProviderType), nullable=False)
    base_url = Column(String(500), nullable=False)
    models_endpoint = Column(String(500), default="/models")
    is_enabled = Column(Boolean, default=True)
    health_status = Column(SQLEnum(HealthStatus), default=HealthStatus.UNKNOWN)
    last_health_check = Column(DateTime, nullable=True)
    last_health_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    api_keys = relationship("APIKey", back_populates="provider", cascade="all, delete-orphan")


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False)  # Store hashed key
    key_prefix = Column(String(20), nullable=False)  # First few chars for identification
    is_enabled = Column(Boolean, default=True)
    health_status = Column(SQLEnum(HealthStatus), default=HealthStatus.UNKNOWN)
    last_health_check = Column(DateTime, nullable=True)
    last_health_error = Column(Text, nullable=True)
    models_cache = Column(Text, nullable=True)  # JSON cached models list
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    provider = relationship("Provider", back_populates="api_keys")


# Pydantic models for API
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    user: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter"]] = None


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage
    system_fingerprint: Optional[str] = None


# Provider management models
class ProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    type: ProviderType
    base_url: HttpUrl
    models_endpoint: str = "/models"
    is_enabled: bool = True


class ProviderUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=200)
    base_url: Optional[HttpUrl] = None
    models_endpoint: Optional[str] = None
    is_enabled: Optional[bool] = None


class ProviderResponse(BaseModel):
    id: int
    name: str
    display_name: str
    type: ProviderType
    base_url: str
    models_endpoint: str
    is_enabled: bool
    health_status: HealthStatus
    last_health_check: Optional[datetime]
    last_health_error: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    provider_id: int
    name: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=10)  # The actual key, will be hashed


class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    is_enabled: Optional[bool] = None


class APIKeyResponse(BaseModel):
    id: int
    provider_id: int
    name: str
    key_prefix: str
    is_enabled: bool
    health_status: HealthStatus
    last_health_check: Optional[datetime]
    last_health_error: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    provider_id: int
    provider_name: str
    status: HealthStatus
    checked_at: datetime
    error: Optional[str] = None
    models_count: Optional[int] = None
    latency_ms: Optional[int] = None
