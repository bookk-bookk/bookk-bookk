from typing import Callable

from http import HTTPStatus
import pytest
from slack.web.slack_response import SlackResponse

from app import slack_client


@pytest.fixture
def book_submit_data() -> Callable:
    def _book_submit_data(bookstore_url: str) -> dict:
        return {
            "type": "dialog_submission",
            "submission": {
                "category": "경제일반",
                "bookstore_url": bookstore_url,
                "recommend_reason": "죽도록 일해서 돈을 벌고, 아끼고, 모으는 것만으로는 절대 젊어서 부자가 될 수 없다고 말하며, ‘젊어서 부자가 되는 길’을 공개한다.",
            },
            "callback_id": "bookk-bookk",
            "state": "Limo",
            "team": {"id": "T1ABCD2E12", "domain": "coverbands"},
            "user": {"id": "W12A3BCDEF", "name": "dreamweaver"},
            "channel": {"id": "C1AB2C3DE", "name": "coverthon-1999"},
            "action_ts": "936893340.702759",
            "token": "M1AqUUw3FqayAbqNtsGMch72",
            "response_url": "https://hooks.slack.com/app/T012AB0A1/123456789/JpmK0yzoZDeRiqfeduTBYXWQ",
        }

    return _book_submit_data


@pytest.fixture
def user_profile_success_data() -> dict:
    return {
        "ok": True,
        "profile": {
            "avatar_hash": "ge3b51ca72de",
            "status_text": "Print is dead",
            "status_emoji": ":books:",
            "status_expiration": 0,
            "real_name": "Egon Spengler",
            "display_name": "spengler",
            "real_name_normalized": "Egon Spengler",
            "display_name_normalized": "spengler",
            "email": "spengler@ghostbusters.example.com",
            "image_original": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "team": "T012AB3C4",
        },
    }


@pytest.fixture
def ok_response_from_slack():
    def _ok_response_from_slack(response_data: dict) -> SlackResponse:
        return SlackResponse(
            client=slack_client,
            http_verb="http",
            api_url="url",
            data=response_data,
            headers={},
            req_args={},
            status_code=int(HTTPStatus.OK),
        )

    return _ok_response_from_slack


@pytest.fixture
def chat_post_success_data() -> dict:
    return {
        "ok": True,
        "channel": "C1H9RESGL",
        "ts": "1503435956.000247",
        "message": {
            "text": "Here's a message for you",
            "username": "ecto1",
            "bot_id": "B19LU7CSY",
            "attachments": [{"text": "This is an attachment", "id": 1, "fallback": "This is an attachment's fallback"}],
            "type": "message",
            "subtype": "bot_message",
            "ts": "1503435956.000247",
        },
    }


@pytest.fixture
def yes24_opengraph_tags() -> dict:
    return {
        "openGraph": {
            "title": "부의 추월차선 (10주년 스페셜 에디션) - 예스24",
            "description": "미국 아마존 금융ㆍ사업 분야 1위 국내 유명서점 10년간 종합 베스트셀러가장 빠르게 부자 되는 새로운 공식을 제시해 큰 반향 불러일으킨 책부자 되기 방식의 패러다임을 바꾼 〈부의 추월차선〉이 독자들의 사랑과 지지 속에 한국 출간 10주년을 맞이했다. 이 책은 ...",
            "type": "book",
            "image": {"url": "https://image.yes24.com/goods/106369008/XL"},
            "url": "https://www.yes24.com/Product/Goods/106369008",
            "site_name": "예스24",
        }
    }


@pytest.fixture
def ridibooks_opengraph_tags() -> dict:
    return {
        "openGraph": {
            "title": "부의 추월차선(10주년 기념 에디션)",
            "description": "부의 추월차선(10주년 기념 에디션) 작품소개: 미국 아마존 금융ㆍ사업 분야 1위국내 유명서점 10년간 종합 베스트셀러가장 빠르게 부자 되는 새로운 공식을 제시해 큰 반향 불러일으킨 책부자 되기 방식의 패러다임을 바꾼 〈부의 추월차선〉이 독자들의 사랑과 지지 속에 한국 출간 10주년을 맞이했다. 이 책은 죽도록 일하며 수십 년 간 아끼고 모아서 휠체어에 탈 때쯤 부자 되는 40년짜리 플랜을 비웃으며 한 ...",
            "type": "books.book",
            "image": {"url": "https://img.ridicdn.net/cover/1354000126/xxlarge#1"},
            "url": "https://ridibooks.com/books/1354000126",
            "site_name": "리디",
        }
    }
