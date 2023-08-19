from typing import List, Optional

from pydantic import BaseModel

from apps.dtos.book import BookCategories


class DialogOption(BaseModel):
    label: str
    value: str


class DialogOptionGroup(BaseModel):
    label: str
    options: List[DialogOption]


class DialogElement(BaseModel):
    label: str
    name: str
    type: str
    option_groups: Optional[List[DialogOptionGroup]] = None
    subtype: Optional[str] = None

    @classmethod
    def get_book_category_ogs(cls) -> List[DialogOptionGroup]:
        option_groups = []
        for category in BookCategories:
            main, subs = category.value
            group = DialogOptionGroup(label=main, options=[DialogOption(label=sub, value=sub) for sub in subs])
            option_groups.append(group)
        return option_groups


class Dialog(BaseModel):
    title: str
    elements: List[DialogElement]
    submit_label: str = "submit"
    callback_id: str
    notify_on_cancel: bool = True
