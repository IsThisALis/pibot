import asyncio
import json
import sqlite3
from collections import deque
from pathlib import Path
from typing import Any, Optional

from telegram.ext import BasePersistence, PersistenceInput
from telegram.ext._contexttypes import ContextTypes
from telegram.ext._utils.types import BD, CD, UD, CDCData, ConversationDict, ConversationKey


class SetEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return {"__type__": "set", "__items__": list(obj)}
        if isinstance(obj, deque):
            return {"__type__": "deque", "__items__": list(obj)}
        return str(obj)


def _object_hook(dct: dict) -> Any:
    if "__type__" in dct:
        t = dct["__type__"]
        if t == "set":
            return set(dct["__items__"])
        if t == "deque":
            return deque(dct["__items__"])
    return dct


def _serialize(obj: Any) -> str:
    return json.dumps(obj, cls=SetEncoder, ensure_ascii=False)


def _deserialize(data: str) -> Any:
    return json.loads(data, object_hook=_object_hook)


class SQLitePersistence(BasePersistence[UD, CD, BD]):
    def __init__(
        self,
        db_path: Path,
        store_data: Optional[PersistenceInput] = None,
        update_interval: float = 60,
        context_types: Optional[ContextTypes[Any, UD, CD, BD]] = None,
    ):
        super().__init__(store_data=store_data, update_interval=update_interval)
        self.db_path = db_path
        self.context_types = context_types or ContextTypes()
        self._user_data: dict[int, UD] = {}
        self._chat_data: dict[int, CD] = {}
        self._bot_data: Optional[BD] = None
        self._callback_data: Optional[CDCData] = None
        self._conversations: dict[str, dict[ConversationKey, object]] = {}
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persistence (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    async def _store_async(self, key: str, value: Any) -> None:
        serialized = _serialize(value)
        def _sync() -> None:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO persistence (key, value) VALUES (?, ?)",
                    (key, serialized),
                )
        await asyncio.to_thread(_sync)

    async def _load_async(self, key: str) -> Any:
        def _sync() -> Any:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    row = conn.execute(
                        "SELECT value FROM persistence WHERE key = ?", (key,)
                    ).fetchone()
                    if row:
                        return _deserialize(row[0])
                    return None
            except Exception:
                return None
        return await asyncio.to_thread(_sync)

    async def get_user_data(self) -> dict[int, UD]:
        data = await self._load_async("user_data")
        if data:
            self._user_data = {int(k): v for k, v in data.items()}
        return dict(self._user_data)

    async def update_user_data(self, user_id: int, data: UD) -> None:
        self._user_data[user_id] = data
        await self._store_async("user_data", self._user_data)

    async def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        pass

    async def drop_user_data(self, user_id: int) -> None:
        self._user_data.pop(user_id, None)
        await self._store_async("user_data", self._user_data)

    async def get_chat_data(self) -> dict[int, CD]:
        data = await self._load_async("chat_data")
        if data:
            self._chat_data = {int(k): v for k, v in data.items()}
        return dict(self._chat_data)

    async def update_chat_data(self, chat_id: int, data: CD) -> None:
        self._chat_data[chat_id] = data
        await self._store_async("chat_data", self._chat_data)

    async def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        pass

    async def drop_chat_data(self, chat_id: int) -> None:
        self._chat_data.pop(chat_id, None)
        await self._store_async("chat_data", self._chat_data)

    async def get_bot_data(self) -> BD:
        data = await self._load_async("bot_data")
        if data is not None:
            self._bot_data = data
        else:
            self._bot_data = self.context_types.bot_data()
        return self._bot_data  # type: ignore[return-value]

    async def update_bot_data(self, data: BD) -> None:
        self._bot_data = data
        await self._store_async("bot_data", data)

    async def refresh_bot_data(self, bot_data: BD) -> None:
        pass

    async def get_callback_data(self) -> Optional[CDCData]:
        data = await self._load_async("callback_data")
        if data is not None:
            self._callback_data = data
        return self._callback_data

    async def update_callback_data(self, data: CDCData) -> None:
        self._callback_data = data
        await self._store_async("callback_data", data)

    async def get_conversations(self, name: str) -> ConversationDict:
        data = await self._load_async(f"conversations_{name}")
        return data or {}

    async def update_conversation(
        self, name: str, key: ConversationKey, new_state: Optional[object]
    ) -> None:
        conv = self._conversations.setdefault(name, {})
        if new_state is None:
            conv.pop(key, None)
        else:
            conv[key] = new_state
        await self._store_async(f"conversations_{name}", conv)

    async def flush(self) -> None:
        if self._user_data:
            await self._store_async("user_data", self._user_data)
        if self._chat_data:
            await self._store_async("chat_data", self._chat_data)
        if self._bot_data is not None:
            await self._store_async("bot_data", self._bot_data)
        if self._callback_data is not None:
            await self._store_async("callback_data", self._callback_data)
