import os
from typing import Optional

from fastapi import FastAPI, Form
from slack import WebClient

app = FastAPI()

slack_token: Optional[str] = os.environ.get("SLACK_API_TOKEN")
slack_client = WebClient(token=slack_token, run_async=True)

# fmt: off
DIALOG_FORMAT: dict = {
    "callback_id": "test-test-callback",
    "title": "책을 공유해주세요.",
    "submit_label": "submit",
    "notify_on_cancel": True,
    "state": "Limo",
    "elements": [
        {"label": "책 이름", "name": "book_name", "type": "text", },
        {
            "label": "카테고리",
            "name": "categories",
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


@app.post("/open-form/")
async def open_form(trigger_id: str = Form("")) -> str:
    await slack_client.dialog_open(dialog=DIALOG_FORMAT, trigger_id=trigger_id)  # type: ignore
    return "created"
