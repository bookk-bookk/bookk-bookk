import os
import json
from http import HTTPStatus
from typing import Optional

from fastapi import FastAPI, Request, Response
from slack import WebClient
from slack.web.slack_response import SlackResponse
from starlette.datastructures import FormData

app = FastAPI()

slack_token: Optional[str] = os.environ.get("SLACK_API_TOKEN")
slack_client = WebClient(token=slack_token, run_async=True)

DIALOG_SUBMIT_DONE: str = "dialog_submission"

# fmt: off
DIALOG_FORMAT: dict = {
    "callback_id": "test-test-callback",
    "title": "책을 공유해주세요.",
    "submit_label": "submit",
    "notify_on_cancel": True,
    "elements": [
        {"label": "책 이름", "name": "book_name", "type": "text", },
        {
            "label": "카테고리",
            "name": "category",
            "type": "select",
            "option_groups": [
                {
                    "label": "경영/경제",
                    "options": [
                        {"label": "경영일반", "value": "business-common", },
                        {"label": "경제일반", "value": "economics-common", },
                        {"label": "마케팅세일즈", "value": "marketing-sales", },
                    ],
                },
                {
                    "label": "인문/사회/역사",
                    "options": [
                        {"label": "인문", "value": "humanities", },
                        {"label": "정치/사회", "value": "politics-society", },
                        {"label": "예술/문화", "value": "art-culture", },
                    ],
                },
            ],
        },
        {"label": "도서 링크", "name": "link", "type": "text", "subtype": "url", },
        {"label": "추천 이유", "name": "recommend_reason", "type": "textarea", },
        {"label": "출판사", "name": "publisher", "type": "text", },
        {"label": "저자", "name": "author", "type": "text", },
    ],
}
# fmt: on

SUCCESS_MESSAGE: str = """
📖 {username}님의 추천도서를 공유했습니다 📖
{book_name} ({category}, {publisher} 출판, {author} 저)
{link}
{recommend_reason}
"""


@app.post("/open-form/")
async def open_form(request: Request) -> Response:
    form_data: FormData = await request.form()
    response: SlackResponse = await slack_client.dialog_open(  # type: ignore
        dialog=DIALOG_FORMAT, trigger_id=form_data.get("trigger_id"),
    )
    if response["ok"]:
        return Response()
    return Response(content=response["error"])


@app.post("/submit-book/")
async def submit_book(request: Request) -> Response:
    form_data: FormData = await request.form()
    payload: dict = json.loads(form_data.get("payload"))

    if payload.get("type") == DIALOG_SUBMIT_DONE:

        user_profile_res: SlackResponse = await slack_client.users_profile_get(  # type: ignore
            user=payload["user"]["id"],
        )
        if not user_profile_res["ok"]:
            return Response(content=user_profile_res["error"])

        book: dict = payload["submission"]
        post_message_res: SlackResponse = await slack_client.chat_postMessage(  # type: ignore
            channel=payload["channel"]["id"],
            text=SUCCESS_MESSAGE.format(**book, username=user_profile_res["profile"]["real_name"]),
        )
        if not post_message_res["ok"]:
            Response(content=post_message_res["error"])
        return Response()

    return Response(status_code=HTTPStatus.BAD_REQUEST)
