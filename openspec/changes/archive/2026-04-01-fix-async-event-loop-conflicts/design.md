## Context

Hiện tại, ứng dụng Open Notebook sử dụng LangGraph với `SqliteSaver` (sync). LangGraph nodes (`call_model_with_messages`, `call_model_with_source_context`) là các hàm đồng bộ (sync) chứa hack phức tạp: phát hiện event loop đang chạy → spawn `ThreadPoolExecutor` → tạo `asyncio.new_event_loop()` bên trong thread mới → chạy async code (`provision_langchain_model`, `ContextBuilder.build()`). 

FastAPI async endpoint gọi `chat_graph.invoke()` (sync) trực tiếp trong async context. Bên trong `invoke`, node sync lại tạo event loop phụ. Connection Pool SurrealDB (`asyncio.Queue` + `asyncio.Lock`) được tạo trên event loop chính của FastAPI nhưng bị truy cập từ event loop phụ trong thread con → crash `RuntimeError`.

**Kiến trúc hiện tại (có bug):**
```
FastAPI (event loop A)
  → chat_graph.invoke()           # sync, blocks event loop A
    → call_model_with_messages()  # sync node
      → ThreadPoolExecutor()
        → asyncio.new_event_loop()  # event loop B (khác A)
          → provision_langchain_model()
            → model_manager.get_model()
              → db_connection()     # dùng Pool trên event loop A → CRASH
```

**Dependencies đã xác nhận:**
- `langgraph` hỗ trợ `ainvoke()`, `aget_state()`, `astream()`
- `langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver` — có sẵn
- `aiosqlite==0.22.1` — đã cài

## Goals / Non-Goals

**Goals:**
- Loại bỏ hoàn toàn xung đột event loop bằng cách chuyển sang async thuần
- Graph nodes sử dụng async function → LangGraph tự xử lý đúng event loop
- Tất cả callers (`chat.py`, `source_chat.py`, `graph_utils.py`) dùng `ainvoke()` / `aget_state()`
- Connection Pool hoạt động chính xác trên một event loop duy nhất
- Không thay đổi API contract của frontend (cùng endpoints, cùng response format)

**Non-Goals:**
- Không refactor frontend trong change này
- Không thay đổi logic AI prompt/generation
- Không thêm tính năng mới, chỉ sửa lỗi concurrency

## Decisions

### 1. Chuyển graph node sang async function
**Quyết định:** Đổi `call_model_with_messages` → `async def acall_model_with_messages` và `call_model_with_source_context` → `async def acall_model_with_source_context`.

**Lý do:** LangGraph hỗ trợ cả sync và async node. Khi node là async, `graph.ainvoke()` sẽ `await` trực tiếp → không cần ThreadPoolExecutor hay new_event_loop. Toàn bộ code chạy trên event loop chính của FastAPI.

**Thay thế đã xem xét:** Wrap `invoke()` trong `asyncio.to_thread()` — nhưng node bên trong vẫn tạo event loop phụ, vấn đề chéo loop không giải quyết được.

### 2. Dùng AsyncSqliteSaver thay SqliteSaver
**Quyết định:** `from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver` + `aiosqlite`.

**Lý do:** `SqliteSaver.get_state()` là sync. Nếu graph node là async mà dùng sync checkpointer, LangGraph nội bộ sẽ phải wrap trong thread → lại rơi vào vấn đề cũ. `AsyncSqliteSaver` cho phép `aget_state()` chạy thuần async.

### 3. Chia sẻ connection sqlite chung giữa 2 graph
**Quyết định:** Cả `chat.py` (notebook chat) và `source_chat.py` đều dùng chung 1 sqlite checkpoint file (`LANGGRAPH_CHECKPOINT_FILE`). Sẽ tạo **1 shared AsyncSqliteSaver instance** thay vì mỗi module tạo riêng.

**Lý do:** `aiosqlite` dùng connection pool nội bộ, tránh race condition khi 2 module cùng mở file.

### 4. Gọi `ainvoke()` thay `invoke()` ở router layer
**Quyết định:** Trong `api/routers/chat.py` và `api/routers/source_chat.py`:
- `result = await chat_graph.ainvoke(...)` thay cho `chat_graph.invoke(...)` 
- `state = await chat_graph.aget_state(...)` thay cho `asyncio.to_thread(chat_graph.get_state, ...)`

**Lý do:** Loại bỏ hoàn toàn `asyncio.to_thread` workaround. `ainvoke` và `aget_state` hoạt động thuần async trên event loop đang chạy.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| `AsyncSqliteSaver` API khác `SqliteSaver` | Đã xác nhận API tương thích, chỉ khác cách khởi tạo (context manager) |
| `model.invoke(payload)` bên trong node vẫn là sync call (gọi HTTP tới AI provider) | LangChain `BaseChatModel.invoke()` tuy tên là sync nhưng bên trong đã xử lý I/O đúng. Và trong async node, nó sẽ được LangGraph wrap đúng cách. Có thể chuyển sang `await model.ainvoke(payload)` cho sạch hơn |
| SQLite single-writer lock khi nhiều request cùng ghi checkpoint | SQLite WAL mode + aiosqlite đã xử lý. Concurrent reads OK, writes sẽ queue orderly |
| Rollback phức tạp nếu có bug | Giữ nguyên file cũ dưới dạng comment/backup trong commit, có thể revert nhanh |

## Migration Plan

1. Tạo module `open_notebook/graphs/checkpoint.py` chứa shared `AsyncSqliteSaver` instance
2. Sửa `open_notebook/graphs/chat.py`: node async, import shared checkpointer
3. Sửa `open_notebook/graphs/source_chat.py`: node async, import shared checkpointer  
4. Sửa `api/routers/chat.py`: `ainvoke` / `aget_state`
5. Sửa `api/routers/source_chat.py`: `ainvoke` / `aget_state`
6. Sửa `open_notebook/utils/graph_utils.py`: `aget_state`
7. Test local → build Docker → deploy VPS

Rollback: revert commit, redeploy.
