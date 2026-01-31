from typing import Any, Dict, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    when_iso: Optional[str] = None
    channel: Optional[str] = None


class ChatResponse(BaseModel):
    agent_message: str
    metadata: Dict[str, Any]
    ui_trigger: str
    tech_card: Optional[Dict[str, Any]] = None


class SkillSignals(BaseModel):
    message: str
    nlu_keywords: Optional[list[str]] = None
    nlu_entities: Optional[list[str]] = None


class SkillTriageResponse(BaseModel):
    intent: str
    priority: str
    revenue_tier: str


class SkillTerritoryResponse(BaseModel):
    territory_code: str
    zone_id: str
    service_tier: str
    multiplier: float


class SkillAssignResponse(BaseModel):
    tech_id: Optional[str]
    eta_minutes: int
    service_tier: str


class SkillQuoteResponse(BaseModel):
    quote_min: int
    quote_max: int
    currency: str
