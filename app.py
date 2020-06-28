import asyncio
import os
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
from model import book_dialog_format

app = FastAPI()

slack_token: Optional[str] = os.environ.get("SLACK_API_TOKEN")
slack_client = WebClient(token=slack_token, run_async=True)

DIALOG_SUBMIT_DONE: str = "dialog_submission"
SUCCESS_MESSAGE: str = """
📖 {username}님의 추천도서를 공유했습니다 📖
{book_name} ({category}, {publisher} 출판, {author} 저)
{link}
{recommend_reason}
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
        return Response(content=post_message_res["error"])

    # posting to notion is intended to run background.
    asyncio.create_task(post_book_to_notion(book))

    return Response()
