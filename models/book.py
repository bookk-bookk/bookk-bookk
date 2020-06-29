import enum
from dataclasses import dataclass

from models.dialog import DialogOption, DialogOptionGroup


@dataclass(repr=True)
class Book:
    book_name: str
    category: str
    link: str
    publisher: str
    author: str
    recommend_reason: str


class BookCategories(enum.Enum):
    ECONOMIC_BUSINESS = "경영/경제", ("경영일반", "경제일반", "마케팅세일즈")
    HUMANITY_SOCIETY_HISTORY = "인문/사회/역사", ("인문", "정치/사회", "예술/문화")

    @classmethod
    def get_option_groups(cls):
        options_groups = []
        for category in cls:
            main, subs = category.value
            options = [DialogOption(label=sub, value=sub) for sub in subs]
            option_group = DialogOptionGroup(label=main, options=options)
            options_groups.append(option_group)
        return options_groups
