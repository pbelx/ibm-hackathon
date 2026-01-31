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
    signal_text = " ".join(signals.get("keywords", []) + signals.get("entities", []))
    combined_text = f"{message} {signal_text}".strip()

    priority = detect_priority(message, locale)
    if priority != "CRITICAL":
        critical = [k.lower() for k in locale.get("critical_keywords", [])]
        if any(k in signals.get("keywords", []) for k in critical):
            priority = "CRITICAL"
        if "cold room" in signals.get("keywords", []):
            priority = "CRITICAL"

    intent = detect_intent(message, priority)
    revenue_tier = detect_revenue_tier(message, priority)

    territory_result = validate_territory(combined_text, territory)
    required_skill = "cold_room" if any(
        k in combined_text.lower() for k in ["cold room", "chiller"]
    ) else "hvac_ac"
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
