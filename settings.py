import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    slack_api_token: str = os.getenv("SLACK_API_TOKEN")
    og_app_id: str = os.getenv("OG_APP_ID")
    notion_token_v2: str = os.getenv("NOTION_TOKEN_V2")
    notion_page_url: str = os.getenv("NOTION_PAGE_URL")


settings = Settings()
