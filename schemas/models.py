from pydantic import BaseModel, Field


class TrendData(BaseModel):
    topic: str
    velocity: int = Field(ge=0, le=100)
    opportunity: int = Field(ge=0, le=100)
    description: str


class HookData(BaseModel):
    trend_id: str
    hook_text: str
    curiosity_score: int = Field(ge=0, le=100)


class ContentBlueprint(BaseModel):
    hook: HookData
    script: str
    visual_prompt: str
