## 1. Shared Async Checkpointer

- [x] 1.1 Tạo file `open_notebook/graphs/checkpoint.py` với shared `AsyncSqliteSaver` instance dùng `aiosqlite` và `LANGGRAPH_CHECKPOINT_FILE`
- [x] 1.2 Export `get_memory()` async function trả về `AsyncSqliteSaver` singleton (lazy init)

## 2. Chuyển Graph Nodes sang Async

- [x] 2.1 Trong `open_notebook/graphs/chat.py`: đổi `call_model_with_messages(state, config)` thành `async def acall_model_with_messages(state, config)` — gọi `await provision_langchain_model()` trực tiếp, bỏ `new_event_loop` + `ThreadPoolExecutor`
- [x] 2.2 Trong `open_notebook/graphs/chat.py`: chuyển `model.invoke(payload)` sang `await model.ainvoke(payload)` để model call cũng chạy async
- [x] 2.3 Trong `open_notebook/graphs/chat.py`: thay `SqliteSaver` bằng shared `AsyncSqliteSaver` từ `checkpoint.py`, compile graph với async checkpointer
- [x] 2.4 Trong `open_notebook/graphs/source_chat.py`: đổi `call_model_with_source_context` → `async def acall_model_with_source_context` — gọi `await ContextBuilder.build()` và `await provision_langchain_model()` trực tiếp
- [x] 2.5 Trong `open_notebook/graphs/source_chat.py`: chuyển `model.invoke(payload)` sang `await model.ainvoke(payload)`
- [x] 2.6 Trong `open_notebook/graphs/source_chat.py`: thay `SqliteSaver` bằng shared `AsyncSqliteSaver` từ `checkpoint.py`

## 3. Cập nhật Router Layer

- [x] 3.1 Trong `api/routers/chat.py`: thay tất cả `asyncio.to_thread(chat_graph.get_state, ...)` → `await chat_graph.aget_state(...)`
- [x] 3.2 Trong `api/routers/chat.py`: thay `chat_graph.invoke(...)` → `await chat_graph.ainvoke(...)` ở cả endpoint `/chat/execute` và streaming generator `/chat/stream`
- [x] 3.3 Trong `api/routers/source_chat.py`: thay tất cả `asyncio.to_thread(source_chat_graph.get_state, ...)` → `await source_chat_graph.aget_state(...)`
- [x] 3.4 Trong `api/routers/source_chat.py`: thay `source_chat_graph.invoke(...)` → `await source_chat_graph.ainvoke(...)` trong streaming generator
- [x] 3.5 Trong `open_notebook/utils/graph_utils.py`: thay `asyncio.to_thread(graph.get_state, ...)` → `await graph.aget_state(...)`

## 4. Verification

- [x] 4.1 Test local: gửi 1 chat message đơn lẻ thành công (12.1s, không có RuntimeError)
- [x] 4.2 Test concurrent: 10/10 requests thành công (24.2s total, 0 event loop errors)
- [x] 4.3 Build Docker image và deploy lên VPS `160.30.113.168`
- [x] 4.4 Test qua VPS: gửi chat qua VPS xác nhận hoạt động end-to-end
