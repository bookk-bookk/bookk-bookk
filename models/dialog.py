from dataclasses import dataclass
from typing import List, Optional

from models.book import BookCategories


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

    @classmethod
    def get_book_category_ogs(cls) -> List[DialogOptionGroup]:
        option_groups = []
        for category in BookCategories:
            main, subs = category.value
            options = [DialogOption(label=sub, value=sub) for sub in subs]
            group = DialogOptionGroup(label=main, options=options)
            option_groups.append(group)
        return option_groups


book_dialog_format = DialogFormat(
    title="책을 공유해주세요.",
    elements=[
        DialogElement(label="책이름", name="book_name", type="text"),
        DialogElement(label="카테고리", name="category", type="select", option_groups=DialogFormat.get_book_category_ogs()),
        DialogElement(label="도서링크", name="link", type="text", subtype="url"),
        DialogElement(label="출판사", name="publisher", type="text"),
        DialogElement(label="저자", name="author", type="text"),
        DialogElement(label="추천이유", name="recommend_reason", type="textarea"),
    ],
)
