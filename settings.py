import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings


class Settings(BaseSettings):
    slack_api_token: Optional[str] = os.getenv("SLACK_API_TOKEN")
    og_app_id: Optional[str] = os.getenv("OG_APP_ID")
    notion_token_v2: Optional[str] = os.getenv("NOTION_TOKEN_V2")
    notion_page_url: Optional[str] = os.getenv("NOTION_PAGE_URL")


env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)
settings = Settings()
