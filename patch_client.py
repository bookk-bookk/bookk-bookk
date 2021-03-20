import hashlib

from notion.client import NotionClient  # type: ignore
from notion.store import RecordStore  # type: ignore


class RecordStoreWithSmallLimit(RecordStore):
    def call_load_page_chunk(self, page_id):

        if self._client.in_transaction():
            self._pages_to_refresh.append(page_id)
            return

        data = {
            "pageId": page_id,
            "limit": 100,
            "cursor": {"stack": []},
            "chunkNumber": 0,
            "verticalColumns": False,
        }

        recordmap = self._client.post("loadPageChunk", data).json()["recordMap"]

        self.store_recordmap(recordmap)


class NotionClientWithSmallLimit(NotionClient):
    def __init__(self, token_v2, monitor=False, start_monitoring=False, enable_caching=False, cache_key=None):
        super().__init__(
            token_v2=token_v2,
            monitor=monitor,
            start_monitoring=start_monitoring,
            enable_caching=enable_caching,
            cache_key=cache_key,
        )

        if enable_caching:
            cache_key = cache_key or hashlib.sha256(token_v2.encode()).hexdigest()
            self._store = RecordStoreWithSmallLimit(self, cache_key=cache_key)
        else:
            self._store = RecordStoreWithSmallLimit(self)

        self._update_user_info()
