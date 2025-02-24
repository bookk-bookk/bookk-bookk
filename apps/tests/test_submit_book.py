import json
from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from dtos.internal.book import Book
from app import app, SUCCESS_MESSAGE
from settings import settings


client = TestClient(app)


@pytest.mark.asyncio
class TestBookSubmission:
    @pytest.mark.parametrize(
        "invalid_url",
        [
            "https://.",
            "https://..",
            "https://../",
            "https://?",
            "https://??",
            "https://??/",
            "https://#",
            "https://##",
            "https://##/",
            "https://www.example.com##",
            "https://www.example.com##/",
            "example",
            "https//invalid",
        ],
    )
    async def test_submit_book_fail_by_invalid_url_format(self, invalid_url, book_submit_data):
        # When: 잘못된 서점 링크 첨부 시도
        with (
            patch("app.slack_client.users_profile_get") as mock_user_profile,
            patch("app.slack_client.chat_postMessage") as mock_post_message,
        ):
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(book_submit_data(bookstore_url=invalid_url))},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # Then: 도서 정보 저장을 거절한다
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"errors": [{"name": "bookstore_url", "error": "유효하지 않은 URL입니다."}]}

        mock_user_profile.assert_not_called()
        mock_post_message.assert_not_called()

    @pytest.mark.parametrize("bookstore_without_og_tags", ["aladin.co.kr", "kyobobook.co.kr", "book.interpark.com"])
    async def test_submit_book_fail_by_bookstore_without_og_tags(self, bookstore_without_og_tags, book_submit_data):
        # When: 오픈그래프 태그가 없는 서점 홈페이지 링크 첨부 시도
        with (
            patch("app.slack_client.users_profile_get") as mock_user_profile,
            patch("app.slack_client.chat_postMessage") as mock_post_message,
        ):
            url_without_og_tags = f"https://{bookstore_without_og_tags}/books/1354000008?_s=search&_q=부의+추월차선"
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(book_submit_data(bookstore_url=url_without_og_tags))},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # Then: 도서 정보 저장을 거절한다
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"errors": [{"name": "bookstore_url", "error": "첨부 가능한 서점 링크는 리디북스/예스24 입니다."}]}

        mock_user_profile.assert_not_called()
        mock_post_message.assert_not_called()

    @pytest.mark.parametrize(
        "valid_bookstore_url",
        [
            "https://ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "https://www.ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "http://ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "http://www.ridibooks.com/books/1354000008?_s=search&_q=부의+추월차선",
            "https://yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
            "https://www.yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
            "http://yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
            "http://www.yes24.com/Product/Search?domain=BOOK&query=부의+추월차선",
        ],
    )
    async def test_submit_book_succeed(
        self,
        valid_bookstore_url,
        book_submit_data,
        user_profile_success_data,
        chat_post_success_data,
        ok_response_from_slack,
    ):
        # When: 유효한 서점 링크를 첨부하여 도서 추천
        with (
            patch(
                "app.slack_client.users_profile_get",
                AsyncMock(return_value=ok_response_from_slack(user_profile_success_data)),
            ) as mock_user_profile,
            patch(
                "app.slack_client.chat_postMessage",
                AsyncMock(return_value=ok_response_from_slack(chat_post_success_data)),
            ) as mock_post_message,
            patch("app.post_book_to_notion", AsyncMock(return_value=True)) as mock_post_notion,
        ):
            successful_submit_data = book_submit_data(bookstore_url=valid_bookstore_url)
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(successful_submit_data)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        assert response.status_code == HTTPStatus.OK
        assert not response.content

        # Then: 정상적인 절차에 따라 노션에 저장한다
        mock_user_profile.assert_called_once_with(user=successful_submit_data["user"]["id"])
        mock_post_message.assert_called_once_with(
            text=SUCCESS_MESSAGE.format(
                **successful_submit_data["submission"],
                recommender=user_profile_success_data["profile"]["real_name"],
            ),
            channel=successful_submit_data["channel"]["id"],
        )
        mock_post_notion.assert_called_once_with(
            Book(**successful_submit_data["submission"], recommender=user_profile_success_data["profile"]["real_name"]),
        )

    async def test_post_yes24_book_to_notion(
        self,
        user_profile_success_data,
        chat_post_success_data,
        book_submit_data,
        ok_response_from_slack,
        yes24_opengraph_tags,
    ):
        # When: yes24 링크를 첨부하여 도서 추천
        with (
            patch(
                "app.slack_client.users_profile_get",
                AsyncMock(return_value=ok_response_from_slack(user_profile_success_data)),
            ),
            patch(
                "app.slack_client.chat_postMessage",
                AsyncMock(return_value=ok_response_from_slack(chat_post_success_data)),
            ),
            patch("helper.get_og_tags", AsyncMock(return_value=yes24_opengraph_tags)),
            patch("helper.httpx.AsyncClient.post") as mock_post_notion,
        ):
            yes24_url = "https://www.yes24.com/Product/Goods/106369008"
            successful_submit_data = book_submit_data(bookstore_url=yes24_url)
            client.post(
                "/submit-book/",
                data={"payload": json.dumps(successful_submit_data)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # Then: yes24 오픈그래프 태그에서 얻은 정보를 노션에 저장한다
        assert mock_post_notion.await_args_list[0].kwargs["json"] == {
            "parent": {
                "type": "database_id",
                "database_id": settings.notion_database_id,
            },
            "properties": {
                "title": {
                    "title": [
                        {"type": "text", "text": {"content": yes24_opengraph_tags["openGraph"]["title"]}},
                    ]
                },
                "URL": {
                    "type": "url",
                    "url": yes24_url,
                },
                "category": {
                    "multi_select": [
                        {"name": successful_submit_data["submission"]["category"]},
                        {"name": "경영/경제"},
                    ],
                },
                "recommender": {
                    "rich_text": [
                        {"type": "text", "text": {"content": user_profile_success_data["profile"]["real_name"]}}
                    ]
                },
                "recommend_reason": {
                    "rich_text": [
                        {"type": "text", "text": {"content": successful_submit_data["submission"]["recommend_reason"]}}
                    ]
                },
            },
            "children": [
                {
                    "object": "block",
                    "image": {
                        "type": "external",
                        "external": {
                            "url": yes24_opengraph_tags["openGraph"]["image"]["url"].replace("XL", "XL.png"),
                        },
                    },
                },
            ],
        }

    async def test_post_ridibooks_book_to_notion(
        self,
        user_profile_success_data,
        chat_post_success_data,
        book_submit_data,
        ok_response_from_slack,
        ridibooks_opengraph_tags,
    ):
        # When: 리디북스 링크를 첨부하여 도서 추천
        with (
            patch(
                "app.slack_client.users_profile_get",
                AsyncMock(return_value=ok_response_from_slack(user_profile_success_data)),
            ),
            patch(
                "app.slack_client.chat_postMessage",
                AsyncMock(return_value=ok_response_from_slack(chat_post_success_data)),
            ),
            patch("helper.get_og_tags", AsyncMock(return_value=ridibooks_opengraph_tags)),
            patch("helper.httpx.AsyncClient.post") as mock_post_notion,
        ):
            yes24_url = "https://ridibooks.com/books/1354000126"
            successful_submit_data = book_submit_data(bookstore_url=yes24_url)
            client.post(
                "/submit-book/",
                data={"payload": json.dumps(successful_submit_data)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # Then: 리디북스 오픈그래프 태그에서 얻은 정보를 노션에 저장한다
        assert mock_post_notion.await_args_list[0].kwargs["json"] == {
            "parent": {
                "type": "database_id",
                "database_id": settings.notion_database_id,
            },
            "properties": {
                "title": {
                    "title": [
                        {"type": "text", "text": {"content": ridibooks_opengraph_tags["openGraph"]["title"]}},
                    ]
                },
                "URL": {
                    "type": "url",
                    "url": yes24_url,
                },
                "category": {
                    "multi_select": [
                        {"name": successful_submit_data["submission"]["category"]},
                        {"name": "경영/경제"},
                    ],
                },
                "recommender": {
                    "rich_text": [
                        {"type": "text", "text": {"content": user_profile_success_data["profile"]["real_name"]}}
                    ]
                },
                "recommend_reason": {
                    "rich_text": [
                        {"type": "text", "text": {"content": successful_submit_data["submission"]["recommend_reason"]}}
                    ]
                },
            },
            "children": [
                {
                    "object": "block",
                    "image": {
                        "type": "external",
                        "external": {
                            "url": ridibooks_opengraph_tags["openGraph"]["image"]["url"].replace(
                                "xxlarge#1", "xxlarge1.png"
                            )
                        },
                    },
                },
            ],
        }

    async def test_submit_book_fail_to_post_message(
        self, book_submit_data, user_profile_success_data, chat_post_success_data, ok_response_from_slack
    ):
        # Given: 노션 저장 실패
        with (
            patch(
                "app.slack_client.users_profile_get",
                AsyncMock(return_value=ok_response_from_slack(user_profile_success_data)),
            ) as mock_user_profile,
            patch(
                "app.slack_client.chat_postMessage",
                AsyncMock(return_value=ok_response_from_slack(chat_post_success_data)),
            ) as mock_post_message,
            patch("app.post_book_to_notion", AsyncMock(return_value=False)),
        ):
            successful_submit_data = book_submit_data(bookstore_url="https://ridibooks.com/books/1354000008")
            response = client.post(
                "/submit-book/",
                data={"payload": json.dumps(successful_submit_data)},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # Then: 노션 저장에 실패해도 슬랙 채널에 알림 메세지를 전송해야 함
        assert response.status_code == HTTPStatus.OK
        assert not response.content

        mock_user_profile.assert_called_once_with(user=successful_submit_data["user"]["id"])
        mock_post_message.assert_called_once_with(
            text=SUCCESS_MESSAGE.format(
                **successful_submit_data["submission"],
                recommender=user_profile_success_data["profile"]["real_name"],
            ),
            channel=successful_submit_data["channel"]["id"],
        )
