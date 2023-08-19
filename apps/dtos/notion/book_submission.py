from pydantic import BaseModel

from apps.dtos.notion.text import Title, BookUrl, Category, Recommender, RecommendReason
from apps.dtos.notion.database import Database
from apps.dtos.notion.image_block import ImageBlock


class BookSubmissionProperties(BaseModel):

    title: Title
    URL: BookUrl
    category: Category
    recommender: Recommender
    recommend_reason: RecommendReason

    def dict(self, *args, **kwargs):
        # 노션에서 키 이름을 'recommend reason' 으로 요구
        result = super().dict(*args, **kwargs)
        result["recommend reason"] = result["recommend_reason"]
        del result["recommend_reason"]
        return result


class BookSubmission(BaseModel):
    parent: Database
    properties: BookSubmissionProperties
    children: list[ImageBlock]
