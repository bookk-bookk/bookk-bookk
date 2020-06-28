import enum
from dataclasses import dataclass
from typing import List, Optional


@dataclass(repr=True)
class DialogOption:
    label: str
    value: str


@dataclass(repr=True)
class DialogOptionGroup:
    label: str
    options: List[DialogOption]


@dataclass(repr=True)
class DialogElement:
    label: str
    name: str
    type: str
    option_groups: Optional[List[DialogOptionGroup]] = None
    subtype: Optional[str] = None


@dataclass(repr=True, eq=True)
class DialogFormat:
    title: str
    elements: List[DialogElement]
    submit_label: str = "submit"
    callback_id: str = "bookk-bookk"
    notify_on_cancel: bool = True


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


book_dialog_format = DialogFormat(
    title="책을 공유해주세요.",
    elements=[
        DialogElement(label="책이름", name="book_name", type="text"),
        DialogElement(label="카테고리", name="category", type="select", option_groups=BookCategories.get_option_groups()),
        DialogElement(label="도서링크", name="link", type="text", subtype="url"),
        DialogElement(label="출판사", name="publisher", type="text"),
        DialogElement(label="저자", name="author", type="text"),
        DialogElement(label="추천이유", name="recommend_reason", type="textarea"),
    ],
)
