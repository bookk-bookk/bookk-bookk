import json
from http import HTTPStatus
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient
from slack.web.slack_response import SlackResponse

from app import app, SUCCESS_MESSAGE, slack_client
from dtos.slack.book import Book

client = TestClient(app)


@pytest.fixture
def submit_payload():
    return {
        "type": "dialog_submission",
        "submission": {
            "category": "경제일반",
            "link": "https://ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
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


@pytest.fixture
def user_profile_success_data():
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
def chat_post_success_data():
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
    async def test_submit_book_fail_by_wrong_url_1(self, submit_payload):
        submit_payload["submission"]["link"] = "htt://www.google.com"
        with (
            patch("app.slack_client.users_profile_get") as mock_user_profile,
            patch("app.slack_client.chat_postMessage") as mock_post_message,
        ):
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(submit_payload)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"errors": [{"name": "link", "error": "유효하지 않은 URL입니다."}]}

        mock_user_profile.assert_not_called()
        mock_post_message.assert_not_called()

    async def test_submit_book_fail_by_wrong_url_2(self, submit_payload):
        submit_payload["submission"]["link"] = "http://.google.com"
        with (
            patch("app.slack_client.users_profile_get") as mock_user_profile,
            patch("app.slack_client.chat_postMessage") as mock_post_message,
        ):
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(submit_payload)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"errors": [{"name": "link", "error": "유효하지 않은 URL입니다."}]}

        mock_user_profile.assert_not_called()
        mock_post_message.assert_not_called()

    async def test_submit_book_succeed(self, submit_payload, user_profile_success_data, chat_post_success_data):
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
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(submit_payload)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == HTTPStatus.OK
        assert not response.content

        mock_user_profile.assert_called_once_with(user=submit_payload["user"]["id"])
        mock_post_message.assert_called_once_with(
            text=SUCCESS_MESSAGE.format(
                **submit_payload["submission"],
                recommender=user_profile_success_data["profile"]["real_name"],
            ),
            channel=submit_payload["channel"]["id"],
        )
        mock_post_notion.assert_called_once_with(
            Book(**submit_payload["submission"], recommender=user_profile_success_data["profile"]["real_name"]),
        )

    async def test_submit_book_fail_to_post_message(
        self, submit_payload, user_profile_success_data, chat_post_success_data
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
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(submit_payload)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # Then: 슬랙 채널에 알림 메세지 전송하지 않아야 함.
        assert response.status_code == HTTPStatus.OK
        assert not response.content

        mock_user_profile.assert_called_once_with(user=submit_payload["user"]["id"])
        mock_post_message.assert_not_called()
