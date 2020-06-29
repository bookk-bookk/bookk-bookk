import os
import uuid
from asyncio import Future
from http import HTTPStatus

import pytest  # type: ignore

from fastapi.testclient import TestClient
from app import app, slack_client
from forms.dialog import DialogFormat


client = TestClient(app)


@pytest.fixture
def dialog_format():
    # fmt: off
    return {
        "callback_id": "mock-uuid4-hex",
        "title": "책을 공유해주세요.",
        "submit_label": "submit",
        "notify_on_cancel": True,
        "elements": [
            {"label": "책이름", "name": "book_name", "type": "text", "option_groups": None, "subtype": None},
            {
                "label": "카테고리",
                "name": "category",
                "type": "select",
                "option_groups": [
                    {
                        "label": "경영/경제",
                        "options": [
                            {"label": "경영일반", "value": "경영일반", },
                            {"label": "경제일반", "value": "경제일반", },
                            {"label": "마케팅세일즈", "value": "마케팅세일즈", },
                        ],
                    },
                    {
                        "label": "인문/사회/역사",
                        "options": [
                            {"label": "인문", "value": "인문", },
                            {"label": "정치/사회", "value": "정치/사회", },
                            {"label": "예술/문화", "value": "예술/문화", },
                        ],
                    },
                ],
                "subtype": None,
            },
            {"label": "도서링크", "name": "link", "type": "text", "option_groups": None, "subtype": "url"},
            {"label": "출판사", "name": "publisher", "type": "text", "option_groups": None, "subtype": None},
            {"label": "저자", "name": "author", "type": "text", "option_groups": None, "subtype": None},
            {"label": "추천이유", "name": "recommend_reason", "type": "textarea", "option_groups": None, "subtype": None},
        ],
    }
    # fmt: on


@pytest.fixture
def dialog_form_data():
    return {
        "token": "test-token",
        "team_id": "T1234",
        "team_domain": "test-domain",
        "enterprise_id": "E1234",
        "enterprise_name": "Test%20EnterPrice%20Name",
        "channel_id": "C12345678",
        "channel_name": "test",
        "user_id": "U12345678",
        "user_name": "Samantha",
        "command": "/book",
        "text": "test",
        "response_url": "https://hooks.slack.com/commands/1234/5678",
        "trigger_id": "13345224609.738474920.8088930838d88f008e0",
    }


@pytest.fixture
def mock_uuid():
    class UUID4:
        def __init__(self, bytes=os.urandom(16), version=4):
            self.bytes = bytes
            self.version = version
            self.hex = "mock-uuid4-hex"

    return UUID4


@pytest.fixture
def mock_dialog_open_success():
    class TestArgs:
        def __call__(self, *args, **kwargs):
            self.args = list(args)
            self.kwargs = kwargs
            f = Future()
            f.set_result({"ok": True})
            return f

    return TestArgs()


@pytest.fixture
def mock_dialog_open_fail():
    class TestArgs:
        def __call__(self, *args, **kwargs):
            self.args = list(args)
            self.kwargs = kwargs
            f = Future()
            f.set_result({"ok": False, "error": "some-error"})
            return f

    return TestArgs()


def test_open_form_succeed(monkeypatch, dialog_form_data, dialog_format, mock_uuid, mock_dialog_open_success):
    monkeypatch.setattr(slack_client, "dialog_open", mock_dialog_open_success)
    monkeypatch.setattr(uuid, "UUID", mock_uuid)

    response = client.post("/open-form/", data=dialog_form_data)

    assert mock_dialog_open_success.kwargs["trigger_id"] == dialog_form_data["trigger_id"]
    assert DialogFormat(**mock_dialog_open_success.kwargs["dialog"]) == DialogFormat(**dialog_format)
    assert response.status_code == HTTPStatus.OK


def test_open_form_fail(monkeypatch, dialog_form_data, dialog_format, mock_uuid, mock_dialog_open_fail):
    monkeypatch.setattr(slack_client, "dialog_open", mock_dialog_open_fail)
    monkeypatch.setattr(uuid, "UUID", mock_uuid)

    response = client.post("/open-form/", data=dialog_form_data)

    assert mock_dialog_open_fail.kwargs["trigger_id"] == dialog_form_data["trigger_id"]
    assert DialogFormat(**mock_dialog_open_fail.kwargs["dialog"]) == DialogFormat(**dialog_format)
    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "some-error"
