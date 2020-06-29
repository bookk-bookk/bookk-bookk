from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional, List


@dataclass(repr=True)
class Book:
    book_name: str
    category: str
    link: str
    publisher: str
    author: str
    recommend_reason: str


@dataclass(repr=True)
class Category:
    name: str
    sub_categories: Optional[List[Category]]
    main_category: Optional[Category]


class BookCategories(enum.Enum):
    ECONOMIC_BUSINESS = "경영/경제", ("경영일반", "경제일반", "마케팅세일즈")
    HUMANITY_SOCIETY_HISTORY = "인문/사회/역사", ("인문", "정치/사회", "예술/문화")

    @classmethod
    def get_book_categories(cls):
        main_categories = []
        for category in cls:
            main, subs = category.value
            main_category = Category(name=main)
            sub_categories = [Category(name=sub, main_category=main_category) for sub in subs]
            main_category.sub_categories = sub_categories
            main_categories.append(main_category)
        return main_categories
