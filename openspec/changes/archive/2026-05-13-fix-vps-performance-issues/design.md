# Design: Fix VPS Performance Issues

## Overview

Triển khai 3 giải pháp song song để khắc phục vấn đề hiệu suất VPS:
1. **SSE Streaming cho Notebook Chat** (ưu tiên cao nhất)
2. **Client Disconnect Detection** (ưu tiên cao)
3. **SurrealDB Connection Pooling** (ưu tiên trung bình)

## Architecture

### Current Flow (Synchronous Blocking)

```
Frontend → POST /api/chat/execute → chat_graph.invoke() → AI Provider (60-120s)
                                         ↓
                                    Blocks thread pool
                                         ↓
                                    Returns full response
```

### Proposed Flow (SSE Streaming + Disconnect Detection)

```
Frontend → POST /api/chat/stream → StreamingResponse(SSE)
                                       ↓
                                  chat_graph.invoke() → AI Provider
                                       ↓
                                  Yield chunks via SSE ← Check disconnect
                                       ↓
                                  Frontend renders incrementally
```

## Detailed Design

### 1. SSE Streaming for Notebook Chat

**Pattern**: Follow the existing `source_chat.py` streaming implementation.

#### Backend Changes

**File: `api/routers/chat.py`**

Add a new SSE streaming endpoint `/chat/stream`:

```python
@router.post("/chat/stream")
async def stream_chat(request: ExecuteChatRequest):
    """Execute chat with SSE streaming response."""
    # Validate session, build state (same as execute_chat)
    # Return StreamingResponse with SSE generator
    return StreamingResponse(
        stream_notebook_chat_response(
            session_id=full_session_id,
            state_values=state_values,
            model_override=model_override,
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8",
        },
    )
```

The streaming generator function:

```python
async def stream_notebook_chat_response(
    session_id: str, state_values: dict, model_override: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """Stream notebook chat response as SSE events."""
    try:
        # Send user message event
        yield f"data: {json.dumps({'type': 'user_message', ...})}\n\n"

        # Execute graph (invoke is sync, runs in thread)
        result = chat_graph.invoke(...)

        # Stream AI response
        for msg in result.get("messages", []):
            if msg.type == "ai":
                yield f"data: {json.dumps({'type': 'ai_message', 'content': msg.content})}\n\n"

        # Completion signal
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

**Key Decision**: Use `graph.invoke()` (not `graph.astream()`) inside the SSE generator — same pattern as source_chat.py. The streaming benefit comes from SSE keeping the HTTP connection alive with periodic data events, preventing Cloudflare's 100s timeout. True token-by-token streaming from LangChain would be a future enhancement.

#### Frontend Changes

**File: `frontend/src/lib/api/chat.ts`**

Add `streamMessage()` method using `fetch` + `ReadableStream` (same pattern as source-chat.ts):

```typescript
streamMessage: async (
  data: SendNotebookChatMessageRequest,
  onMessage: (event: SSEEvent) => void,
  signal?: AbortSignal
) => {
  const response = await fetch(`${getBaseURL()}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders },
    body: JSON.stringify(data),
    signal,
  })
  // Parse SSE events from ReadableStream
  // Call onMessage for each event
}
```

**File: `frontend/src/lib/hooks/useNotebookChat.ts`**

Update `sendMessage()` to use streaming:
- Replace `chatApi.sendMessage()` with `chatApi.streamMessage()`
- Add `AbortController` for cancel support
- Parse SSE events and update messages incrementally
- Add `cancelChat()` method

### 2. Client Disconnect Detection

**File: `api/routers/chat.py`**

In both the existing `execute_chat` and new `stream_chat` endpoints, add disconnect detection:

```python
from fastapi import Request

@router.post("/chat/stream")
async def stream_chat(request: Request, body: ExecuteChatRequest):
    async def generator():
        while not await request.is_disconnected():
            # Process...
            yield data
        # Client disconnected - cleanup
        logger.info(f"Client disconnected from chat {body.session_id}")
```

This prevents zombie threads from accumulating when users close browser/refresh.

### 3. SurrealDB Connection Pooling

**File: `open_notebook/database/repository.py`**

Replace per-request connection creation with a connection pool:

```python
import asyncio
from asyncio import Queue

class SurrealConnectionPool:
    def __init__(self, max_size: int = 20):
        self._pool: Queue[AsyncSurreal] = Queue(maxsize=max_size)
        self._max_size = max_size
        self._current_size = 0
        self._lock = asyncio.Lock()

    async def acquire(self) -> AsyncSurreal:
        """Get a connection from the pool."""
        try:
            return self._pool.get_nowait()
        except asyncio.QueueEmpty:
            if self._current_size < self._max_size:
                return await self._create_connection()
            # Wait for a connection to be returned
            return await self._pool.get()

    async def release(self, conn: AsyncSurreal):
        """Return a connection to the pool."""
        await self._pool.put(conn)

    async def _create_connection(self) -> AsyncSurreal:
        """Create a new database connection."""
        async with self._lock:
            self._current_size += 1
        db = AsyncSurreal(get_database_url())
        await db.signin({...})
        await db.use(namespace, database)
        return db

# Global pool instance
_pool: Optional[SurrealConnectionPool] = None

async def get_pool() -> SurrealConnectionPool:
    global _pool
    if _pool is None:
        _pool = SurrealConnectionPool(max_size=20)
    return _pool

@asynccontextmanager
async def db_connection():
    pool = await get_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)
```

**Backward Compatibility**: The `db_connection()` context manager signature stays the same — all existing callers work without changes.

## Migration Strategy

1. Add `/chat/stream` endpoint alongside existing `/chat/execute` (non-breaking)
2. Update frontend to use streaming endpoint
3. Keep `/chat/execute` as fallback for any external integrations
4. Deploy connection pool transparently (same API surface)

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| SSE may not work through Cloudflare | Cloudflare supports SSE natively; source_chat already uses it successfully |
| Connection pool stale connections | Add health checks / reconnection on error |
| Breaking existing chat sessions | New endpoint is additive, old endpoint still works |
| Frontend SSE parsing errors | Reuse proven pattern from source_chat frontend code |
