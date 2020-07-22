import asyncio
import json
import uuid
from dataclasses import asdict
from http import HTTPStatus
from typing import Optional

from fastapi import FastAPI, Request, Response
from slack import WebClient
from slack.web.slack_response import SlackResponse
from starlette.datastructures import FormData

from helper import post_book_to_notion
from forms.book import Book
from forms.dialog import book_dialog_format
from settings import settings

app = FastAPI()
event_loop = asyncio.get_event_loop()

slack_token: Optional[str] = settings.slack_api_token
slack_client = WebClient(token=slack_token, run_async=True)


DIALOG_SUBMIT_DONE: str = "dialog_submission"
SUCCESS_MESSAGE: str = """
📖 {username} 님이 추천도서를 공유했습니다 📖
{recommend_reason}
{link}
{category}
"""


@app.post("/open-form/")
async def open_form(request: Request) -> Response:
    form_data: FormData = await request.form()
    book_dialog_format.callback_id = uuid.uuid4().hex
    response: SlackResponse = await slack_client.dialog_open(  # type: ignore
        dialog=asdict(book_dialog_format), trigger_id=form_data.get("trigger_id"),
    )
    if response["ok"]:
        return Response()
    return Response(content=response["error"])


@app.post("/submit-book/")
async def submit_book(request: Request) -> Response:
    form_data: FormData = await request.form()
    payload: dict = json.loads(form_data.get("payload"))

    if payload.get("type") != DIALOG_SUBMIT_DONE:
        return Response(status_code=HTTPStatus.BAD_REQUEST)

    book: Book = Book(**payload["submission"])
    if not book.is_valid_link():
        return Response(
            headers={"content-type": "application/json"},
            content=json.dumps({"errors": [{"name": "link", "error": "유효하지 않은 URL입니다."}]}),
        )

    user_profile_res: SlackResponse = await slack_client.users_profile_get(  # type: ignore
        user=payload["user"]["id"],
    )
    if not user_profile_res["ok"]:
        return Response(content=user_profile_res["error"])

    post_message_res: SlackResponse = await slack_client.chat_postMessage(  # type: ignore
        channel=payload["channel"]["id"],
        text=SUCCESS_MESSAGE.format(**asdict(book), username=user_profile_res["profile"]["real_name"]),
    )
    if not post_message_res["ok"]:
        return Response(content=post_message_res["error"])

    # posting to notion is intended to run background.
    event_loop.call_later(0, post_book_to_notion, book)

    return Response()
