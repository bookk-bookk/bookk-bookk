import json
from asyncio import Future
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app import app, slack_client, SUCCESS_MESSAGE


client = TestClient(app)


@pytest.fixture
def submit_form_data():
    return {
        "payload": json.dumps(
            {
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
        )
    }


@pytest.fixture
def mock_user_profile_get(user_profile):
    class TestArgs:
        def __call__(self, *args, **kwargs):
            self.args = list(args)
            self.kwargs = kwargs
            f = Future()
            f.set_result(user_profile)
            return f

    return TestArgs()


@pytest.fixture
def mock_post_message(post_result):
    class TestArgs:
        def __call__(self, *args, **kwargs):
            self.args = list(args)
            self.kwargs = kwargs
            f = Future()
            f.set_result(post_result)
            return f

    return TestArgs()


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


@pytest.mark.parametrize("user_profile", [USER_PROFILE_SUCCESS_BODY])
@pytest.mark.parametrize("post_result", [POST_MESSAGE_SUCCESS_BODY])
def test_submit_book_succeed(monkeypatch, submit_form_data, mock_user_profile_get, mock_post_message):
    monkeypatch.setattr(slack_client, "users_profile_get", mock_user_profile_get)
    monkeypatch.setattr(slack_client, "chat_postMessage", mock_post_message)
    payload_from_user = json.loads(submit_form_data["payload"])

    response = client.post("/submit-book/", data=submit_form_data)

    assert mock_user_profile_get.kwargs["user"] == payload_from_user["user"]["id"]

    assert mock_post_message.kwargs["channel"] == payload_from_user["channel"]["id"]
    assert mock_post_message.kwargs["text"] == SUCCESS_MESSAGE.format(
        **payload_from_user["submission"], username=USER_PROFILE_SUCCESS_BODY["profile"]["real_name"],
    )

    assert response.status_code == HTTPStatus.OK
    assert not response.content


@pytest.mark.parametrize("user_profile", [USER_PROFILE_FAIL_BODY])
def test_submit_book_fail_to_get_user_profile(monkeypatch, submit_form_data, mock_user_profile_get):
    monkeypatch.setattr(slack_client, "users_profile_get", mock_user_profile_get)
    payload_from_user = json.loads(submit_form_data["payload"])

    response = client.post("/submit-book/", data=submit_form_data)

    assert mock_user_profile_get.kwargs["user"] == payload_from_user["user"]["id"]

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == USER_PROFILE_FAIL_BODY["error"]


@pytest.mark.parametrize("user_profile", [USER_PROFILE_SUCCESS_BODY])
@pytest.mark.parametrize("post_result", [POST_MESSAGE_FAIL_BODY])
def test_submit_book_fail_to_post_message(monkeypatch, submit_form_data, mock_user_profile_get, mock_post_message):
    monkeypatch.setattr(slack_client, "users_profile_get", mock_user_profile_get)
    monkeypatch.setattr(slack_client, "chat_postMessage", mock_post_message)
    payload_from_user = json.loads(submit_form_data["payload"])

    response = client.post("/submit-book/", data=submit_form_data)

    assert mock_user_profile_get.kwargs["user"] == payload_from_user["user"]["id"]

    assert mock_post_message.kwargs["channel"] == payload_from_user["channel"]["id"]
    assert mock_post_message.kwargs["text"] == SUCCESS_MESSAGE.format(
        **payload_from_user["submission"], username=USER_PROFILE_SUCCESS_BODY["profile"]["real_name"],
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == POST_MESSAGE_FAIL_BODY["error"]
