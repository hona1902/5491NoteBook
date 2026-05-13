"""Shared async LangGraph checkpointer.

Provides a single AsyncSqliteSaver instance used by both the notebook chat
graph and the source-chat graph so they share the same checkpoint file
without conflicting SQLite connections.
"""

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from open_notebook.config import LANGGRAPH_CHECKPOINT_FILE

_memory: AsyncSqliteSaver | None = None


async def get_memory() -> AsyncSqliteSaver:
    """Return the global AsyncSqliteSaver singleton (lazy-initialised)."""
    global _memory
    if _memory is None:
        conn = await aiosqlite.connect(
            LANGGRAPH_CHECKPOINT_FILE,
        )
        _memory = AsyncSqliteSaver(conn)
    return _memory
