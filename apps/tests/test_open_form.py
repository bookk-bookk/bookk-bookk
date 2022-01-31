import os
from asyncio import Future
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest  # type: ignore

from fastapi.testclient import TestClient
from apps.app import app, slack_client


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
            {
                "label": "카테고리",
                "name": "category",
                "type": "select",
                "option_groups": [
                    {
                        "label": "경영/경제",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("경영일반", "경제일반", "통계/회계", "마케팅/세일즈", "기업경영/리더십", "재테크/금융/부동산")
                        ],
                    },
                    {
                        "label": "인문/사회",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("사회일반", "인문일반", "페미니즘", "외교/정치", "인권/사회", "역사/문학")
                        ],
                    },
                    {
                        "label": "예술/문화",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("미술", "음악", "건축", "무용", "사진", "영화", "만화", "디자인")
                        ],
                    },
                    {
                        "label": "자기계발",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("취업/창업", "삶의 자세", "기획/리더십", "설득/화술/협상", "인간관계/처세술")
                        ],
                    },
                    {
                        "label": "시/에세이",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("시", "에세이")
                        ],
                    },
                    {
                        "label": "소설",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("고전", "현대", "역사", "동화", "판타지", "SF")
                        ],
                    },
                    {
                        "label": "여행",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("국내", "해외")
                        ],
                    },
                    {
                        "label": "종교",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("종교일반", "불교", "개신교", "천주교", "힌두교", "가톨릭교", "이슬람교", "기타 종교")
                        ],
                    },
                    {
                        "label": "외국어",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("영어일반", "어학시험", "생활영어", "비즈니스영어", "기타 외국어")
                        ],
                    },
                    {
                        "label": "수학/과학/공학",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("수학", "공학", "자연과학", "응용과학")
                        ],
                    },
                    {
                        "label": "컴퓨터/IT",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("IT자격증", "IT비즈니스", "컴퓨터공학/이론", "개발/프로그래밍")
                        ],
                    },
                    {
                        "label": "건강/취미",
                        "options": [
                            {"label": c, "value": c, }
                            for c in ("생활습관", "음식/요리", "운동/스포츠", "기타")
                        ],
                    },
                ],
                "subtype": None,
            },
            {"label": "도서링크", "name": "link", "type": "text", "option_groups": None, "subtype": "url"},
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
def mock_dialog_open(response):
    f = Future()
    f.set_result(response)
    return f


@pytest.mark.parametrize("response", [{"ok": True, "error": ""}])
def test_open_form_succeed(mocker, dialog_form_data, dialog_format, mock_uuid, mock_dialog_open):
    mocker.patch("app.slack_client.dialog_open", MagicMock(return_value=mock_dialog_open))
    mocker.patch("uuid.UUID", mock_uuid)

    response = client.post("/open-form/", json=dialog_form_data)
    assert response.status_code == HTTPStatus.OK

    slack_client.dialog_open.assert_called_once_with(trigger_id=dialog_form_data["trigger_id"], dialog=dialog_format)


@pytest.mark.parametrize("response", [{"ok": False, "error": "some-error"}])
def test_open_form_fail(mocker, dialog_form_data, dialog_format, mock_uuid, mock_dialog_open):
    mocker.patch("app.slack_client.dialog_open", MagicMock(return_value=mock_dialog_open))
    mocker.patch("uuid.UUID", mock_uuid)

    response = client.post("/open-form/", json=dialog_form_data)

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "some-error"

    slack_client.dialog_open.assert_called_once_with(trigger_id=dialog_form_data["trigger_id"], dialog=dialog_format)
