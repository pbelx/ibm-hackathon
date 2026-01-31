import os
from pathlib import Path
from dotenv import load_dotenv


class Settings:
    def __init__(self) -> None:
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=env_path)
        self.APP_ENV = os.getenv("APP_ENV", "dev")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.NLU_API_KEY = os.getenv("NLU_API_KEY", "")
        self.NLU_URL = os.getenv("NLU_URL", "")
        self.NLU_VERSION = os.getenv("NLU_VERSION", "2022-08-10")
        self.WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
        self.WATSONX_URL = os.getenv("WATSONX_URL", "")
        self.WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
        self.WATSONX_MODEL_ID = os.getenv("WATSONX_MODEL_ID", "")
        self.WATSONX_VERSION = os.getenv("WATSONX_VERSION", "2024-05-31")


settings = Settings()
