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
