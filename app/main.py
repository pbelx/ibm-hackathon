from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .data.load import load_locale, load_techs, load_territory
from .db import init_db
from .integrations.nlu_client import build_nlu_client
from .settings import settings

app = FastAPI(title="Universal Dispatcher API")


@app.on_event("startup")
def startup() -> None:
    app.state.locale = load_locale()
    app.state.territory = load_territory()
    app.state.techs = load_techs()
    app.state.nlu_client = None
    if settings.NLU_API_KEY and settings.NLU_URL:
        app.state.nlu_client = build_nlu_client(
            api_key=settings.NLU_API_KEY,
            url=settings.NLU_URL,
            version=settings.NLU_VERSION,
        )
    init_db()


if settings.APP_ENV == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)
