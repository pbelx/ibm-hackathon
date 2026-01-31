from fastapi import APIRouter, Request

from .db import Lead, SessionLocal
from .domain.orchestrator import handle_chat
from .integrations.nlu_client import analyze_text, nlu_to_signals
from .models import ChatRequest, ChatResponse

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):
    signals = {"keywords": [], "entities": []}
    nlu_error = None
    nlu_client = request.app.state.nlu_client
    if nlu_client:
        try:
            nlu_json = analyze_text(nlu_client, req.message)
            signals = nlu_to_signals(nlu_json)
        except Exception as exc:
            nlu_error = str(exc)

    response = handle_chat(
        message=req.message,
        when_iso=req.when_iso,
        locale=request.app.state.locale,
        territory=request.app.state.territory,
        techs=request.app.state.techs,
        signals=signals,
    )

    if signals["keywords"] or signals["entities"]:
        response["metadata"]["nlu_keywords"] = signals["keywords"]
        response["metadata"]["nlu_entities"] = signals["entities"]
    if nlu_error:
        response["metadata"]["nlu_error"] = nlu_error

    metadata = response["metadata"]
    lead = Lead(
        customer_message=req.message,
        intent=metadata.get("intent"),
        priority=metadata.get("priority"),
        revenue_tier=metadata.get("revenue_tier"),
        territory_code=metadata.get("territory_code"),
        zone_id=metadata.get("zone_id"),
        service_tier=metadata.get("service_tier"),
        tech_assigned=metadata.get("tech_assigned"),
        quote_min=metadata.get("quote_min"),
        quote_max=metadata.get("quote_max"),
        status="new",
    )

    db = SessionLocal()
    try:
        db.add(lead)
        db.commit()
    finally:
        db.close()

    return response


@router.get("/leads")
def get_leads() -> list[dict]:
    db = SessionLocal()
    try:
        leads = (
            db.query(Lead)
            .order_by(Lead.created_at.desc())
            .limit(50)
            .all()
        )
        return [lead.to_dict() for lead in leads]
    finally:
        db.close()
