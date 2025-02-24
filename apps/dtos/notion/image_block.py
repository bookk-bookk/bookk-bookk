from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel

from enums import BookStoreImageDomain


class ImageUrl(BaseModel):
    url: str

    @property
    def _image_domain(self) -> BookStoreImageDomain:
        parsed_url = urlparse(self.url)
        for domain in BookStoreImageDomain:
            if domain in parsed_url.netloc or domain in parsed_url.path:
                return domain

    def model_post_init(self, __context: Any):
        if self._image_domain is BookStoreImageDomain.RIDI:
            # https://img.ridicdn.net/cover/1354000126/xxlarge#1 -> https://img.ridicdn.net/cover/1354000126/xxlarge1.png
            self.url = self.url.replace("xxlarge#1", "xxlarge1.png")
        elif self._image_domain is BookStoreImageDomain.YES_TWENTY_FOUR:
            # https://image.yes24.com/goods/142763152/XL -> https://image.yes24.com/goods/142763152/XL.png
            self.url = self.url.replace("XL", "XL.png")


class Image(BaseModel):
    type: str = "external"
    external: ImageUrl


class ImageBlock(BaseModel):
    object: str = "block"
    image: Image
