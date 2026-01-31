from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import (
    EntitiesOptions,
    Features,
    KeywordsOptions,
)


def build_nlu_client(api_key: str | None, url: str | None, version: str) -> NaturalLanguageUnderstandingV1:
    if not api_key or not url:
        raise RuntimeError("Missing NLU_API_KEY or NLU_URL")

    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(version=version, authenticator=authenticator)
    nlu.set_service_url(url)
    return nlu


def analyze_text(nlu: NaturalLanguageUnderstandingV1, text: str) -> dict:
    response = nlu.analyze(
        text=text,
        features=Features(
            keywords=KeywordsOptions(limit=8),
            entities=EntitiesOptions(limit=8),
        ),
    ).get_result()
    return response


def nlu_to_signals(nlu_json: dict) -> dict:
    keywords = [k.get("text", "").lower() for k in nlu_json.get("keywords", [])]
    entities = [e.get("text", "").lower() for e in nlu_json.get("entities", [])]
    return {"keywords": [k for k in keywords if k], "entities": [e for e in entities if e]}
