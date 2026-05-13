## 1. SurrealDB Connection Pooling

- [x] 1.1 Implement `SurrealConnectionPool` class in `open_notebook/database/repository.py` with async Queue-based pool, configurable `max_size` (default 20), lazy initialization, and global singleton via `get_pool()`
- [x] 1.2 Add stale connection detection: wrap pool `acquire()` to test connection health; discard and recreate on failure
- [x] 1.3 Replace `db_connection()` context manager internals to use pool `acquire()`/`release()` instead of creating new `AsyncSurreal` per call — keep the same `async with db_connection() as conn:` API surface
- [x] 1.4 Verify all existing repo_* functions (repo_query, repo_create, repo_update, repo_delete, repo_insert, repo_upsert, repo_relate) work without changes on top of the pooled `db_connection()`

## 2. Backend SSE Streaming Endpoint

- [x] 2.1 Add `stream_notebook_chat_response()` async generator in `api/routers/chat.py` — follow the proven pattern from `api/routers/source_chat.py::stream_source_chat_response()`
- [x] 2.2 Add `POST /api/chat/stream` endpoint in `api/routers/chat.py` returning `StreamingResponse` with SSE headers (`Cache-Control: no-cache`, `Connection: keep-alive`, `Content-Type: text/plain; charset=utf-8`)
- [x] 2.3 Integrate client disconnect detection: accept `Request` parameter in `stream_chat()` and check `await request.is_disconnected()` within the SSE generator loop; log disconnect with session ID and break

## 3. Frontend Streaming Integration

- [x] 3.1 Add `streamMessage()` method to `frontend/src/lib/api/chat.ts` using `fetch` + `ReadableStream` with SSE parsing, `AbortSignal` support, and `onMessage` callback — follow the pattern from source-chat frontend
- [x] 3.2 Update `useNotebookChat` hook (or equivalent chat hook) to call `chatApi.streamMessage()` instead of `chatApi.sendMessage()`, with `AbortController` for cancel, incremental message state updates from SSE events, and a `cancelChat()` method

## 4. Testing & Deployment

- [x] 4.1 Test locally: send a chat message and verify SSE events are received in browser DevTools (Network tab → EventStream)
- [x] 4.2 Test disconnect: start a chat, close the tab, and verify backend logs the disconnect and frees the thread
- [x] 4.3 Test concurrent load: open 3+ simultaneous chat sessions and verify the server does NOT freeze — all sessions respond and DB connections are pooled
- [x] 4.4 Build Docker image and deploy to VPS `160.30.113.168` — verify the fix through Cloudflare at `sotay5491.io.vn`
