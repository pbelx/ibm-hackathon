from fastapi import APIRouter, Request

from .db import Lead, SessionLocal
from .domain.orchestrator import handle_chat
from .integrations.nlu_client import analyze_text, nlu_to_signals
from .integrations.watsonx_client import generate_message
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

    try:
        response["agent_message"] = generate_message(
            api_key=request.app.state.settings.WATSONX_API_KEY,
            base_url=request.app.state.settings.WATSONX_URL,
            project_id=request.app.state.settings.WATSONX_PROJECT_ID,
            model_id=request.app.state.settings.WATSONX_MODEL_ID,
            user_message=req.message,
            metadata=response["metadata"],
            version=request.app.state.settings.WATSONX_VERSION,
        )
        response["metadata"]["watsonx_used"] = True
    except Exception as exc:
        response["metadata"]["watsonx_error"] = str(exc)
        response["metadata"]["watsonx_used"] = False

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


@router.get("/watsonx/test")
def watsonx_test(request: Request) -> dict:
    try:
        msg = generate_message(
            api_key=request.app.state.settings.WATSONX_API_KEY,
            base_url=request.app.state.settings.WATSONX_URL,
            project_id=request.app.state.settings.WATSONX_PROJECT_ID,
            model_id=request.app.state.settings.WATSONX_MODEL_ID,
            user_message="Test message for watsonx.",
            metadata={"priority": "NORMAL"},
            version=request.app.state.settings.WATSONX_VERSION,
        )
        return {"status": "ok", "message": msg}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
