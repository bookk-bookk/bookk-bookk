import json
from http import HTTPStatus
from typing import Callable
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from slack.web.slack_response import SlackResponse
from dtos.internal.book import Book
from app import app, SUCCESS_MESSAGE, slack_client

client = TestClient(app)


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


@pytest.mark.asyncio
class TestBookSubmission:
    @pytest.mark.parametrize(
        "invalid_url",
        [
            "https://.",
            "https://..",
            "https://../",
            "https://?",
            "https://??",
            "https://??/",
            "https://#",
            "https://##",
            "https://##/",
            "https://www.example.com##",
            "https://www.example.com##/",
            "example",
            "https//invalid",
        ],
    )
    async def test_submit_book_fail_by_invalid_url_format(self, invalid_url, book_submit_data):
        with (
            patch("app.slack_client.users_profile_get") as mock_user_profile,
            patch("app.slack_client.chat_postMessage") as mock_post_message,
        ):
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(book_submit_data(bookstore_url=invalid_url))},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"errors": [{"name": "bookstore_url", "error": "유효하지 않은 URL입니다."}]}

        mock_user_profile.assert_not_called()
        mock_post_message.assert_not_called()

    @pytest.mark.parametrize("bookstore_without_og_tags", ["aladin.co.kr", "kyobobook.co.kr", "book.interpark.com"])
    async def test_submit_book_fail_by_bookstore_without_og_tags(self, bookstore_without_og_tags, book_submit_data):
        with (
            patch("app.slack_client.users_profile_get") as mock_user_profile,
            patch("app.slack_client.chat_postMessage") as mock_post_message,
        ):
            url_without_og_tags = f"https://{bookstore_without_og_tags}/books/1354000008?_s=search&_q=부의+추월차선"
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(book_submit_data(bookstore_url=url_without_og_tags))},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"errors": [{"name": "bookstore_url", "error": "첨부 가능한 서점 링크는 리디북스/예스24 입니다."}]}

        mock_user_profile.assert_not_called()
        mock_post_message.assert_not_called()

    @pytest.mark.parametrize(
        "valid_bookstore_url",
        [
            "https://ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "https://www.ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "http://ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "http://www.ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "https://yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
            "https://www.yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
            "http://yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
            "http://www.yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
        ],
    )
    async def test_submit_book_succeed(
        self, valid_bookstore_url, book_submit_data, user_profile_success_data, chat_post_success_data
    ):
        with (
            patch(
                "app.slack_client.users_profile_get",
                AsyncMock(
                    return_value=SlackResponse(
                        client=slack_client,
                        http_verb="http",
                        api_url="url",
                        data=user_profile_success_data,
                        headers={},
                        req_args={},
                        status_code=int(HTTPStatus.OK),
                    )
                ),
            ) as mock_user_profile,
            patch(
                "app.slack_client.chat_postMessage",
                AsyncMock(
                    return_value=SlackResponse(
                        client=slack_client,
                        http_verb="http",
                        api_url="url",
                        data=chat_post_success_data,
                        headers={},
                        req_args={},
                        status_code=int(HTTPStatus.OK),
                    )
                ),
            ) as mock_post_message,
            patch("app.post_book_to_notion", AsyncMock(return_value=True)) as mock_post_notion,
        ):
            successful_submit_data = book_submit_data(bookstore_url=valid_bookstore_url)
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(successful_submit_data)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == HTTPStatus.OK
        assert not response.content

        mock_user_profile.assert_called_once_with(user=successful_submit_data["user"]["id"])
        mock_post_message.assert_called_once_with(
            text=SUCCESS_MESSAGE.format(
                **successful_submit_data["submission"],
                recommender=user_profile_success_data["profile"]["real_name"],
            ),
            channel=successful_submit_data["channel"]["id"],
        )
        mock_post_notion.assert_called_once_with(
            Book(**successful_submit_data["submission"], recommender=user_profile_success_data["profile"]["real_name"]),
        )

    async def test_submit_book_fail_to_post_message(
        self, book_submit_data, user_profile_success_data, chat_post_success_data
    ):
        # Given: 노션 저장 실패.
        with (
            patch(
                "app.slack_client.users_profile_get",
                AsyncMock(
                    return_value=SlackResponse(
                        client=slack_client,
                        http_verb="http",
                        api_url="url",
                        data=user_profile_success_data,
                        headers={},
                        req_args={},
                        status_code=int(HTTPStatus.OK),
                    )
                ),
            ) as mock_user_profile,
            patch(
                "app.slack_client.chat_postMessage",
                AsyncMock(
                    return_value=SlackResponse(
                        client=slack_client,
                        http_verb="http",
                        api_url="url",
                        data=chat_post_success_data,
                        headers={},
                        req_args={},
                        status_code=int(HTTPStatus.OK),
                    )
                ),
            ) as mock_post_message,
            patch("app.post_book_to_notion", AsyncMock(return_value=False)),
        ):
            successful_submit_data = book_submit_data(bookstore_url="https://ridibooks.com/books/1354000008")
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(successful_submit_data)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # Then: 노션 저장에 실패해도 슬랙 채널에 알림 메세지를 전송해야 함.
        assert response.status_code == HTTPStatus.OK
        assert not response.content

        mock_user_profile.assert_called_once_with(user=successful_submit_data["user"]["id"])
        mock_post_message.assert_called_once_with(
            text=SUCCESS_MESSAGE.format(
                **successful_submit_data["submission"],
                recommender=user_profile_success_data["profile"]["real_name"],
            ),
            channel=successful_submit_data["channel"]["id"],
        )
