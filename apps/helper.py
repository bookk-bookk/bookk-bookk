import logging
from http import HTTPStatus

import httpx
from urllib.parse import quote_plus, urljoin

from httpx import HTTPError

from dtos.notion.book_submission import BookSubmission, BookSubmissionProperties
from dtos.notion.database import Database
from dtos.notion.image_block import ImageBlock, Image, ImageUrl
from dtos.notion.text import (
    Title,
    TextContent,
    Content,
    BookUrl,
    Category,
    CategoryName,
    Recommender,
    RecommendReason,
)
from settings import settings
from dtos.slack.book import Book

OPEN_GRAPH_BASE_URL: str = "https://opengraph.io/api/1.1/site/{book_link}"
NOTION_API_BASE_URL = "https://api.notion.com"


logger = logging.getLogger(__name__)


async def get_og_tags(book_link: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            OPEN_GRAPH_BASE_URL.format(book_link=quote_plus(book_link, encoding="UTF-8")),
            params={"app_id": settings.og_app_id},  # type: ignore
            timeout=60,
        )
    return response.json()


async def post_book_to_notion(book: Book) -> bool:
    response = await get_og_tags(book.link)
    try:
        og_tags = response["openGraph"]
    except KeyError:
        logger.error("Failed to parse OpenGraph::{}".format(response))
        return False

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                urljoin(NOTION_API_BASE_URL, "v1/pages/"),
                headers={"Authorization": f"Bearer {settings.notion_secret_key}", "Notion-Version": "2022-06-28"},
                json=BookSubmission(
                    parent=Database(),
                    properties=BookSubmissionProperties(
                        title=Title(title=[TextContent(text=Content(content=og_tags["title"]))]),
                        URL=BookUrl(url=book.link),
                        category=Category(
                            multi_select=[CategoryName(name=book.category), CategoryName(name=book.parent_category)],
                        ),
                        recommender=Recommender(rich_text=[TextContent(text=Content(content=book.recommender))]),
                        recommend_reason=RecommendReason(
                            rich_text=[TextContent(text=Content(content=book.recommend_reason))],
                        ),
                    ),
                    children=[ImageBlock(image=Image(external=ImageUrl(url=og_tags["image"]["url"])))],
                ).dict(),
            )
        except HTTPError as e:
            logger.error(f"exception occurred while posting notion: {e}")
            return False

        if response.status_code != HTTPStatus.OK:
            logger.error(f"unexpected response from Notion API server: {response.text}")
            return False

    return True
