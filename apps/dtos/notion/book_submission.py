from pydantic import BaseModel, Field

from dtos.notion.text import Title, BookUrl, Category, Recommender, RecommendReason
from dtos.notion.database import Database
from dtos.notion.image_block import ImageBlock


class BookSubmissionProperties(BaseModel):
    title: Title
    URL: BookUrl
    category: Category
    recommender: Recommender
    recommend_reason: RecommendReason = Field(serialization_alias="recommend reason")


class BookSubmission(BaseModel):
    parent: Database
    properties: BookSubmissionProperties
    children: list[ImageBlock]
