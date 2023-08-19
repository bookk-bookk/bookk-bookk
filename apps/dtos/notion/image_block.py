from pydantic import BaseModel


class ImageUrl(BaseModel):
    url: str


class Image(BaseModel):
    type: str = "external"
    external: ImageUrl


class ImageBlock(BaseModel):
    object: str = "block"
    image: Image
