from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TrendData(BaseModel):
    id: Optional[UUID] = Field(default_factory=UUID, alias="id")
    trend_title: str
    trend_summary: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    niche: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Hook(BaseModel):
    id: Optional[UUID] = Field(default_factory=UUID, alias="id")
    trend_id: UUID
    hook_text: str
    emotion: Optional[str] = None
    pattern: Optional[str] = None
    viral_score: Optional[int] = Field(None, ge=1, le=100)
    reasoning: Optional[str] = None
    model_used: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Reflection(BaseModel):
    id: Optional[UUID] = Field(default_factory=UUID, alias="id")
    hook_id: UUID
    performance_score: Optional[int] = Field(None, ge=1, le=100)
    lesson: Optional[str] = None
    reasoning_update: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class StrategyMemory(BaseModel):
    id: Optional[UUID] = Field(default_factory=UUID, alias="id")
    niche: Optional[str] = None
    dominant_emotion: Optional[str] = None
    recommended_pattern: Optional[str] = None
    confidence: Optional[int] = Field(None, ge=1, le=100)
    reasoning: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Analytics(BaseModel):
    id: Optional[UUID] = Field(default_factory=UUID, alias="id")
    hook_id: UUID
    views: Optional[int] = Field(0, ge=0)
    likes: Optional[int] = Field(0, ge=0)
    shares: Optional[int] = Field(0, ge=0)
    comments: Optional[int] = Field(0, ge=0)
    engagement_rate: Optional[float] = Field(None, ge=0.0)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
