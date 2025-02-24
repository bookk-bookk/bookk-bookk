import json
import uuid
from http import HTTPStatus
from typing import Optional, Annotated

from fastapi import FastAPI, Response, Form
from slack import WebClient
from starlette.background import BackgroundTasks
from starlette.requests import Request

from dtos.internal.book import Book
from dtos.slack.book_submission import BookSubmitPayload
from dtos.slack.dialog import Dialog, DialogElement
from dtos.slack.api_repsponse import CommonResponse
from dtos.slack.api_repsponse import UserProfileResponse
from helper import post_book_to_notion
from settings import settings

app = FastAPI()

slack_token: Optional[str] = settings.slack_api_token
slack_client = WebClient(token=slack_token, run_async=True)

DIALOG_SUBMIT_DONE: str = "dialog_submission"
SUCCESS_MESSAGE: str = """
📖 {recommender}님이 {category}도서를 추천했어요 📖

{recommend_reason}
{bookstore_url}
"""


@app.post("/open-form/")
async def open_form(trigger_id: Annotated[str, Form()]) -> Response:
    response = CommonResponse.parse_obj(
        (
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
                        DialogElement(label="도서링크", name="bookstore_url", type="text", subtype="url"),
                        DialogElement(label="추천이유", name="recommend_reason", type="textarea"),
                    ],
                ).dict(),
                trigger_id=trigger_id,
            )
        ).data,
    )

    if response.ok:
        return Response()
    return Response(content=response.error)


@app.post("/submit-book/")
async def submit_book(request: Request, background_tasks: BackgroundTasks) -> Response:
    # json 형태의 폼 데이터는 pydantic 모델 타입으로 어노테이션 했을 때 장점을 누리기 어려우므로 Request 타입으로 어노테이션
    form = await request.form()
    payload: BookSubmitPayload = BookSubmitPayload.parse_obj(json.loads(form.get("payload")))
    if payload.type != DIALOG_SUBMIT_DONE:
        return Response(status_code=HTTPStatus.BAD_REQUEST)

    if not payload.submission.validate_link():
        return Response(
            headers={"content-type": "application/json"},
            content=json.dumps({"errors": [{"name": "bookstore_url", "error": "유효하지 않은 URL입니다."}]}),
        )

    if not payload.submission.able_to_get_opengraph_tags():
        return Response(
            headers={"content-type": "application/json"},
            content=json.dumps({"errors": [{"name": "bookstore_url", "error": "첨부 가능한 서점 링크는 리디북스/예스24 입니다."}]}),
        )

    user_profile_res: UserProfileResponse = UserProfileResponse.parse_obj(
        (await slack_client.users_profile_get(user=payload.user.id)).data,
    )
    book: Book = Book(
        category=payload.submission.category,
        bookstore_url=payload.submission.bookstore_url,
        recommend_reason=payload.submission.recommend_reason,
        recommender=user_profile_res.profile.real_name,
    )

    post_message_res = CommonResponse.parse_obj(
        (
            await slack_client.chat_postMessage(channel=payload.channel.id, text=SUCCESS_MESSAGE.format(**book.dict()))
        ).data,
    )
    if not post_message_res.ok:
        return Response(content=post_message_res.error)

    background_tasks.add_task(post_book_to_notion, book)
    return Response()
