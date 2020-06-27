import aiohttp
import os
from urllib.parse import quote_plus

OPEN_GRAPH_BASE_URL: str = "https://opengraph.io/api/1.1/site/{book_link}"


async def get_og_tags(book_link):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            OPEN_GRAPH_BASE_URL.format(book_link=quote_plus(book_link, encoding="UTF-8")),
            params={"app_id": os.environ.get("OG_APP_ID")},
        ) as response:
            return await response.json()["openGraph"]
