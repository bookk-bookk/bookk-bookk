import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    slack_api_token: str = os.getenv("SLACK_API_TOKEN")
    og_app_id: str = os.getenv("OG_APP_ID")
    books_channel: str = os.getenv("BOOKS_CHANNEL")

    notion_secret_key: str = os.getenv("NOTION_SECRET_KEY")
    notion_database_id: str = os.getenv("NOTION_DATABASE_ID")


if os.getenv("BOOKK_ENV") != "test":
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(dotenv_path=env_path)

settings = Settings()
