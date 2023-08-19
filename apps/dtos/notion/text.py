from pydantic import BaseModel


class Content(BaseModel):
    content: str


class TextContent(BaseModel):
    type: str = "text"
    text: Content


class Title(BaseModel):
    title: list[TextContent]


class BookUrl(BaseModel):
    type: str = "url"
    url: str


class CategoryName(BaseModel):
    name: str


class Category(BaseModel):
    multi_select: list[CategoryName]


class Recommender(BaseModel):
    rich_text: list[TextContent]


class RecommendReason(BaseModel):
    rich_text: list[TextContent]
