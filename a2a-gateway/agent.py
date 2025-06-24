import logging
import os
from typing import Any, AsyncIterable

import httpx
from pydantic import BaseModel, Field
from starlette_context import context

logger = logging.getLogger(__name__)


class AppIdAgent:
    def __init__(self, app_id: str):
        self._app_id = app_id
        self._base_url = os.getenv("BASE_URL", "http://localhost:8080")
        # self._client: httpx.AsyncClient = httpx.AsyncClient(
        #     base_url=self._base_url, timeout=30, headers=self._headers
        # )

    async def invoke(self) -> str:
        return f"--- {self._app_id} --- Hello World"

    async def stream(
        self, query: str, session_id: str | None = None
    ) -> AsyncIterable[Any]:
        logger.info(
            f"AppId.stream - {self._app_id} - query: {query}, session_id: {session_id}"
        )

        logger.debug(f"--- {context['X-API-Key']} ---")

        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "mock content",
        }

        yield {
            "is_task_complete": True,
            "require_user_input": False,
            "content": "Finished!",
        }
