import asyncio
import json
import uuid
from http import HTTPStatus
from typing import Optional

from fastapi import FastAPI, Response
from slack import WebClient

from apps.helper import post_book_to_notion
from apps.forms.book import SubmitRequest, UserProfileResponse, SlackResponse, SubmitRequestPayload
from apps.forms.dialog import DialogTrigger, Dialog, DialogElement
from apps.settings import settings

app = FastAPI()
event_loop = asyncio.get_event_loop()

slack_token: Optional[str] = settings.slack_api_token
slack_client = WebClient(token=slack_token, run_async=True)

DIALOG_SUBMIT_DONE: str = "dialog_submission"
SUCCESS_MESSAGE: str = """
📖 {recommender}님이 {category}도서를 추천했어요 📖

{recommend_reason}
{link}
"""


@app.post("/open-form/")
async def open_form(request: DialogTrigger) -> Response:
    response = SlackResponse.parse_obj(
        await slack_client.dialog_open(  # type: ignore
            dialog=Dialog(
                title="책을 공유해주세요.",
                callback_id=uuid.uuid4().hex,
                elements=[
                    DialogElement(
                        label="카테고리",
                        name="category",
                        type="select",
                        option_groups=DialogElement.get_book_category_ogs(),
                    ),
                    DialogElement(label="도서링크", name="link", type="text", subtype="url"),
                    DialogElement(label="추천이유", name="recommend_reason", type="textarea"),
                ],
            ).dict(),
            trigger_id=request.trigger_id,
        )
    )

    if response.ok:
        return Response()
    return Response(content=response.error)


@app.post("/submit-book/")
async def submit_book(request: SubmitRequest) -> Response:
    payload = SubmitRequestPayload.parse_raw(request.payload)
    if payload.type != DIALOG_SUBMIT_DONE:
        return Response(status_code=HTTPStatus.BAD_REQUEST)

    book = payload.submission
    if not book.validate_link():
        return Response(
            headers={"content-type": "application/json"},
            content=json.dumps({"errors": [{"name": "link", "error": "유효하지 않은 URL입니다."}]}),
        )

    user_profile_res = UserProfileResponse.parse_obj(
        await slack_client.users_profile_get(  # type: ignore
            user=payload.user.id,
        )
    )

    book.recommender = user_profile_res.profile.real_name

    post_message_res = SlackResponse.parse_obj(
        await slack_client.chat_postMessage(  # type: ignore
            channel=payload.channel.id, text=SUCCESS_MESSAGE.format(**book.dict()),
        )
    )
    if not post_message_res.ok:
        return Response(content=post_message_res.error)

    # posting to notion is intended to run background.
    event_loop.call_later(0, post_book_to_notion, book)

    return Response()
