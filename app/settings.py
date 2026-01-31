import os
from dotenv import load_dotenv


class Settings:
    def __init__(self) -> None:
        load_dotenv()
        self.APP_ENV = os.getenv("APP_ENV", "dev")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.NLU_API_KEY = os.getenv("NLU_API_KEY", "")
        self.NLU_URL = os.getenv("NLU_URL", "")
        self.NLU_VERSION = os.getenv("NLU_VERSION", "2022-08-10")


settings = Settings()
