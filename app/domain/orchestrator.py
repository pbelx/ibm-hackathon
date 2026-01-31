from .triage import detect_intent, detect_priority, detect_revenue_tier
from .tools import calculate_quote_range, check_tech_availability, validate_territory


def handle_chat(
    message: str,
    when_iso: str | None,
    locale: dict,
    territory: dict,
    techs: dict,
    signals: dict | None = None,
) -> dict:
    signals = signals or {"keywords": [], "entities": []}
    keywords = [k.lower() for k in signals.get("keywords", [])]
    entities = [e.lower() for e in signals.get("entities", [])]
    signal_text = " ".join(keywords + entities)
    combined_text = signal_text or message

    critical_terms = {
        "cold room",
        "server room",
        "warehouse",
        "export",
        "chiller",
        "compressor down",
    }
    priority = "CRITICAL" if any(t in signal_text for t in critical_terms) else "NORMAL"

    maintenance_terms = {"maintenance", "service", "clean", "tune-up", "inspection"}
    if priority == "CRITICAL":
        intent = "emergency_repair"
    elif any(t in signal_text for t in maintenance_terms):
        intent = "maintenance"
    else:
        intent = "general_inquiry"

    commercial_terms = {"warehouse", "hotel", "export"}
    revenue_tier = "high" if priority == "CRITICAL" or any(
        t in signal_text for t in commercial_terms
    ) else "low"

    territory_result = validate_territory(combined_text, territory)
    cold_terms = {"cold room", "chiller", "freezer"}
    required_skill = "cold_room" if any(t in signal_text for t in cold_terms) else "hvac_ac"
    tech = check_tech_availability(
        required_skill, territory_result["service_tier"], techs
    )

    quote = calculate_quote_range(
        problem_type=intent,
        priority=priority,
        tier_multiplier=territory_result["multiplier"],
        locale=locale,
    )

    tech_name = tech.get("display_name", "a technician")
    tech_location = tech.get("base_location", {}).get("name", "your area")
    agent_message = (
        f"I understand. I am dispatching {tech_name} now. "
        f"They are near {tech_location}. We will keep you updated."
    )

    ui_trigger = (
        "show_technician_card"
        if tech and intent == "emergency_repair"
        else "none"
    )

    return {
        "agent_message": agent_message,
        "metadata": {
            "intent": intent,
            "priority": priority,
            "revenue_tier": revenue_tier,
            "territory_code": territory_result["territory_code"],
            "zone_id": territory_result["zone_id"],
            "service_tier": territory_result["service_tier"],
            "tech_assigned": tech.get("tech_id"),
            "quote_min": quote["min"],
            "quote_max": quote["max"],
            "currency": quote["currency"],
        },
        "ui_trigger": ui_trigger,
    }
