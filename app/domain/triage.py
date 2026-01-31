def detect_priority(message: str, locale: dict) -> str:
    critical = locale.get("critical_keywords", [])
    message_lower = message.lower()
    if any(k in message_lower for k in critical):
        return "CRITICAL"
    return "NORMAL"


def detect_intent(message: str, priority: str) -> str:
    message_lower = message.lower()
    if priority == "CRITICAL":
        return "emergency_repair"
    if any(k in message_lower for k in ["service", "maintenance", "clean"]):
        return "maintenance"
    return "general_inquiry"


def detect_revenue_tier(message: str, priority: str) -> str:
    if priority == "CRITICAL":
        return "high"
    return "low"
