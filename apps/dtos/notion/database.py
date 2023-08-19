from pydantic import BaseModel

from apps.settings import settings


class Database(BaseModel):
    type: str = "database_id"
    database_id: str = settings.notion_database_id
