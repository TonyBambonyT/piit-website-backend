import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    TEACHERS_URI: str = os.getenv("TEACHERS_URI")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR")
    CUR_UNITS_URI: str = os.getenv("CUR_UNITS_URI")
    SUBJECTS_URI: str = os.getenv("SUBJECTS_URI")
    STUB_GROUPS_URI: str = os.getenv("STUB_GROUPS_URI")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEFAULT_ARTICLE_ICON: str = os.getenv("DEFAULT_ARTICLE_ICON")

    @property
    def database_url(self) -> str:
        if not all([self.POSTGRES_HOST, self.POSTGRES_DB, self.POSTGRES_USER, self.POSTGRES_PASSWORD]):
            raise RuntimeError("Не все переменные окружения для базы данных установлены")

        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}" \
               f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
