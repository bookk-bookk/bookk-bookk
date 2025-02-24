from typing import Optional

from pydantic import BaseModel

from enums import BookCategories


class Book(BaseModel):
    category: str
    bookstore_url: str
    recommend_reason: str
    recommender: str

    @property
    def parent_category(self) -> Optional[str]:
        for category in BookCategories:
            main, subs = category.value
            for s in subs:
                if s == self.category:
                    return main
        return None
