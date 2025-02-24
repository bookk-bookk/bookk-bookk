from pydantic import BaseModel, Field


class ImageUrl(BaseModel):
    url: str


class OpenGraph(BaseModel):
    title: str
    image: ImageUrl


class OpenGraphIOResponse(BaseModel):
    open_graph: OpenGraph = Field(alias="openGraph")
