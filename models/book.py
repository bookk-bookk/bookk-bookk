from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional


class BookCategories(enum.Enum):
    ECONOMIC_BUSINESS = "경영/경제", ("경영일반", "경제일반", "마케팅세일즈")
    HUMANITY_SOCIETY_HISTORY = "인문/사회/역사", ("인문", "정치/사회", "예술/문화")


@dataclass(repr=True)
class Book:
    book_name: str
    category: str
    link: str
    publisher: str
    author: str
    recommend_reason: str

    @property
    def parent_category(self) -> Optional[str]:
        for category in BookCategories:
            main, subs = category.value
            for s in subs:
                if s == self.category:
                    return main
        return None
