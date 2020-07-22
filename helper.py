from typing import Optional

import requests
from urllib.parse import quote_plus

from notion.block import ImageBlock  # type: ignore
from notion.client import NotionClient  # type: ignore

from settings import settings
from forms.book import Book

OPEN_GRAPH_BASE_URL: str = "https://opengraph.io/api/1.1/site/{book_link}"


def get_og_tags(book_link: str) -> dict:
    response = requests.get(
        OPEN_GRAPH_BASE_URL.format(book_link=quote_plus(book_link, encoding="UTF-8")),
        params={"app_id": settings.og_app_id},  # type: ignore
    )
    return response.json()


notion_client: NotionClient = NotionClient(token_v2=settings.notion_token_v2)
notion_page_url: Optional[str] = settings.notion_page_url


def post_book_to_notion(book: Book) -> None:
    page = notion_client.get_collection_view(notion_page_url)
    new_row = page.collection.add_row()

    new_row.category = [book.category, book.parent_category]
    new_row.URL = book.link
    new_row.recommend_reason = book.recommend_reason
    new_row.recommender = book.recommender

    response = get_og_tags(book.link)

    new_row.title = response["openGraph"]["title"]

    image_block = new_row.children.add_new(ImageBlock)
    image_block.set_source_url(response["openGraph"]["image"]["url"])
