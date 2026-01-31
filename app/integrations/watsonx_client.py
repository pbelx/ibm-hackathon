from __future__ import annotations

import time
from typing import Any

import requests

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"


def _get_iam_token(api_key: str) -> str:
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(IAM_TOKEN_URL, data=data, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def generate_message(
    api_key: str,
    base_url: str,
    project_id: str,
    model_id: str,
    user_message: str,
    metadata: dict,
    version: str,
) -> str:
    if not api_key or not base_url or not project_id or not model_id or not version:
        raise RuntimeError(
            "Missing WATSONX_API_KEY, WATSONX_URL, WATSONX_PROJECT_ID, "
            "WATSONX_MODEL_ID, or WATSONX_VERSION"
        )

    token = _get_iam_token(api_key)
    url = f"{base_url.rstrip('/')}/ml/v1/text/generation?version={version}"
    prompt = (
        "System: You are a helpful dispatch assistant. Write 2 to 4 short sentences, "
        "maximum 60 words. Must include ETA minutes and ask for a location pin or nearby landmark. "
        "Be empathetic and action-focused. Do not add extra commentary. "
        "Return only the message text.\n"
        f"User message: {user_message}\n"
        f"Dispatch details: {metadata}\n"
        "Message:"
    )
    payload: dict[str, Any] = {
        "model_id": model_id,
        "project_id": project_id,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "temperature": 0.3,
            "max_new_tokens": 90,
            "min_new_tokens": 20,
            "stop_sequences": ["\n"],
        },
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    start = time.time()
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if not resp.ok:
        raise RuntimeError(f"watsonx error {resp.status_code}: {resp.text}")
    data = resp.json()
    results = data.get("results", [])
    if not results:
        raise RuntimeError("No generation results from watsonx.ai")
    text = results[0].get("generated_text", "").strip()
    if not text:
        raise RuntimeError("Empty response from watsonx.ai")
    if text.lower() in {"do not comment.", "no other text."}:
        raise RuntimeError("Unusable response from watsonx.ai")
    return text
