import json
from asyncio import Future
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest  # type: ignore
from fastapi.testclient import TestClient

from app import app, slack_client, SUCCESS_MESSAGE, event_loop
from forms.book import Book

client = TestClient(app)


@pytest.fixture
def mock_user_profile_get(user_profile):
    f = Future()
    f.set_result(user_profile)
    return f


@pytest.fixture
def mock_post_message(post_result):
    f = Future()
    f.set_result(post_result)
    return f


@pytest.fixture
def submit_payload():
    return {
        "type": "dialog_submission",
        "submission": {
            "book_name": "부의 추월차선",
            "category": "경제일반",
            "link": "https://ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "publisher": "토트",
            "author": "엠제이 드마코",
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


USER_PROFILE_SUCCESS_BODY = {
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


POST_MESSAGE_SUCCESS_BODY = {
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


USER_PROFILE_FAIL_BODY = {
    "ok": False,
    "error": "user_not_found",
}

POST_MESSAGE_FAIL_BODY = {
    "ok": False,
    "error": "too_many_attachments",
}


def test_submit_book_fail_by_wrong_url_1(mocker, submit_payload):
    mocker.patch("app.slack_client.users_profile_get")
    mocker.patch("app.slack_client.chat_postMessage")
    mocker.patch("app.event_loop.call_later")

    submit_payload["submission"]["link"] = "htt://www.google.com"
    response = client.post("/submit-book/", data={"payload": json.dumps(submit_payload)})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"errors": [{"name": "link", "error": "유효하지 않은 URL입니다."}]}

    slack_client.users_profile_get.assert_not_called()
    slack_client.chat_postMessage.assert_not_called()
    event_loop.call_later.assert_not_called()


def test_submit_book_fail_by_wrong_url_2(mocker, submit_payload):
    mocker.patch("app.slack_client.users_profile_get")
    mocker.patch("app.slack_client.chat_postMessage")
    mocker.patch("app.event_loop.call_later")

    submit_payload["submission"]["link"] = "://www.google.com"
    response = client.post("/submit-book/", data={"payload": json.dumps(submit_payload)})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"errors": [{"name": "link", "error": "유효하지 않은 URL입니다."}]}

    slack_client.users_profile_get.assert_not_called()
    slack_client.chat_postMessage.assert_not_called()
    event_loop.call_later.assert_not_called()


@pytest.mark.parametrize("user_profile", [USER_PROFILE_SUCCESS_BODY])
@pytest.mark.parametrize("post_result", [POST_MESSAGE_SUCCESS_BODY])
def test_submit_book_succeed(mocker, submit_payload, mock_user_profile_get, mock_post_message):
    mocker.patch("app.slack_client.users_profile_get", MagicMock(return_value=mock_user_profile_get))
    mocker.patch("app.slack_client.chat_postMessage", MagicMock(return_value=mock_post_message))
    mocker.patch("app.post_book_to_notion")
    mocker.patch("app.event_loop.call_later")

    response = client.post("/submit-book/", data={"payload": json.dumps(submit_payload)})

    assert response.status_code == HTTPStatus.OK
    assert not response.content

    slack_client.users_profile_get.assert_called_once_with(user=submit_payload["user"]["id"])
    slack_client.chat_postMessage.assert_called_once_with(
        text=SUCCESS_MESSAGE.format(
            **submit_payload["submission"], username=USER_PROFILE_SUCCESS_BODY["profile"]["real_name"],
        ),
        channel=submit_payload["channel"]["id"],
    )
    from app import post_book_to_notion

    event_loop.call_later.assert_called_once_with(0, post_book_to_notion, Book(**submit_payload["submission"]))


@pytest.mark.parametrize("user_profile", [USER_PROFILE_FAIL_BODY])
@pytest.mark.parametrize("post_result", [])
def test_submit_book_fail_to_get_user_profile(mocker, submit_payload, mock_user_profile_get, mock_post_message):
    mocker.patch("app.slack_client.users_profile_get", MagicMock(return_value=mock_user_profile_get))
    mocker.patch("app.slack_client.chat_postMessage", MagicMock(return_value=mock_post_message))
    mocker.patch("app.event_loop.call_later")

    response = client.post("/submit-book/", data={"payload": json.dumps(submit_payload)})

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == USER_PROFILE_FAIL_BODY["error"]

    slack_client.users_profile_get.assert_called_once_with(user=submit_payload["user"]["id"])
    slack_client.chat_postMessage.assert_not_called()
    event_loop.call_later.assert_not_called()


@pytest.mark.parametrize("user_profile", [USER_PROFILE_SUCCESS_BODY])
@pytest.mark.parametrize("post_result", [POST_MESSAGE_FAIL_BODY])
def test_submit_book_fail_to_post_message(mocker, submit_payload, mock_user_profile_get, mock_post_message):
    mocker.patch("app.slack_client.users_profile_get", MagicMock(return_value=mock_user_profile_get))
    mocker.patch("app.slack_client.chat_postMessage", MagicMock(return_value=mock_post_message))
    mocker.patch("app.event_loop.call_later")

    response = client.post("/submit-book/", data={"payload": json.dumps(submit_payload)})

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == POST_MESSAGE_FAIL_BODY["error"]

    slack_client.users_profile_get.assert_called_once_with(user=submit_payload["user"]["id"])
    slack_client.chat_postMessage.assert_called_once_with(
        text=SUCCESS_MESSAGE.format(
            **submit_payload["submission"], username=USER_PROFILE_SUCCESS_BODY["profile"]["real_name"],
        ),
        channel=submit_payload["channel"]["id"],
    )
    event_loop.call_later.assert_not_called()
