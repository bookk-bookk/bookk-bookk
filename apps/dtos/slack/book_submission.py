from enum import Enum
from re import match
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel


LINK_REGEX = (
    r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]"
    r"+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"
)


class BookStoreDomain(str, Enum):
    RIDI = "ridibooks.com"
    YES_TWENTY_FOUR = "yes24.com"


class BookSubmission(BaseModel):
    category: str
    bookstore_url: str
    recommend_reason: str

    def validate_link(self) -> Optional[str]:
        matched = match(LINK_REGEX, self.bookstore_url)
        if not matched:
            return None

        self.bookstore_url = self.bookstore_url.strip()
        return self.bookstore_url

    def able_to_get_opengraph_tags(self) -> bool:
        parsed_link = urlparse(self.bookstore_url)
        for domain in BookStoreDomain:
            if domain in parsed_link.netloc or domain in parsed_link.path:
                return True
        return False


class Identifier(BaseModel):
    id: str


class BookSubmitPayload(BaseModel):
    type: str
    submission: BookSubmission
    user: Identifier
    channel: Identifier
