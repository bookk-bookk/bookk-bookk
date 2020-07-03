from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional


class BookCategories(enum.Enum):
    ECONOMIC_BUSINESS = "경영/경제", ("경영일반", "경제일반", "통계/회계", "마케팅/세일즈", "기업경영/리더십", "재테크/금융/부동산")
    HUMANITY_SOCIETY = "인문/사회", ("사회일반", "인문일반", "페미니즘", "외교/정치", "인권/사회", "역사/문학")
    ART_CULTURE = "예술/문화", ("미술", "음악", "건축", "무용", "사진", "영화", "만화", "디자인")
    SELF_DEVELOP = "자기계발", ("취업/칭업", "삶의 자세", "기획/리더십", "설득/화술/협상", "인간관계/처세술")
    ESSAY_POEM = "시/에세이", ("시", "에세이")
    NOVEL = "소설", ("고전", "현대", "역사", "동화", "판타지", "SF")
    TRIP = "여행", ("국내", "해외")
    RELIGION = "종교", ("종교일반", "불교", "개신교", "천주교", "힌두교", "가톨릭교", "이슬람교", "기타")
    FOREIGN_LANGUAGE = "외국어", ("영어일반", "어학시험", "생활영어", "비즈니스영어", "기타")
    MATH_SCIENCE_ENGINEERING = "수학/과학/공학", ("수학", "공학", "자연과학", "응용과학")
    COMPUTER_IT = "컴퓨터/IT", ("IT자격증", "IT비즈니스", "컴퓨터공학/이론", "개발/프로그래밍")
    HEALTH_HOBBY = "건강/취미", ("생활습관", "음식/요리", "운동/스포츠", "기타")


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
