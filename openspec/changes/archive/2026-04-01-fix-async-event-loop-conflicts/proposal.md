## Why

Khi nhiều người dùng chat đồng thời, Backend bị crash với lỗi `RuntimeError: cannot be called from a running event loop` và `Task attached to a different loop`. Nguyên nhân gốc: LangGraph `chat_graph.invoke()` là hàm đồng bộ (sync) được gọi trực tiếp bên trong FastAPI async context. Bên trong hàm đó, `call_model_with_messages()` lại tạo thêm event loop mới (`asyncio.new_event_loop()`) rồi chạy `concurrent.futures.ThreadPoolExecutor` để gọi async code — dẫn đến xung đột event loop chéo luồng khi Connection Pool (dùng `asyncio.Queue` + `asyncio.Lock`) bị truy cập từ nhiều event loop khác nhau. Bài test 10 request đồng thời cho kết quả chỉ 1/10 thành công, 9/10 crash ngay lập tức.

## What Changes

- Chuyển graph node `call_model_with_messages` từ sync sang async (`acall_model_with_messages`) để loại bỏ hoàn toàn việc tạo event loop phụ
- Chuyển graph node `call_model_with_source_context` từ sync sang async tương tự
- Thay `chat_graph.invoke()` bằng `await chat_graph.ainvoke()` trong cả endpoint `/chat/execute` và streaming generator `/chat/stream`
- Thay `source_chat_graph.invoke()` bằng `await source_chat_graph.ainvoke()` trong streaming generator
- Loại bỏ tất cả pattern `asyncio.to_thread(graph.get_state)` → thay bằng `await graph.aget_state()`
- Nâng cấp `SqliteSaver` sang `AsyncSqliteSaver` (từ `langgraph.checkpoint.sqlite.aio`) để hỗ trợ async checkpointing
- Đảm bảo `SurrealConnectionPool` trong `repository.py` hoạt động đúng trên một event loop duy nhất của FastAPI

## Capabilities

### New Capabilities
- `async-graph-execution`: Chuyển toàn bộ LangGraph execution sang native async, loại bỏ xung đột event loop chéo luồng

### Modified Capabilities
_(Không có spec cũ nào cần sửa requirement)_

## Impact

- **`open_notebook/graphs/chat.py`**: Chuyển `call_model_with_messages` sang async, dùng `AsyncSqliteSaver`
- **`open_notebook/graphs/source_chat.py`**: Chuyển `call_model_with_source_context` sang async, dùng `AsyncSqliteSaver`
- **`api/routers/chat.py`**: Thay `chat_graph.invoke()` → `await chat_graph.ainvoke()`, `asyncio.to_thread(get_state)` → `await aget_state()`
- **`api/routers/source_chat.py`**: Thay `source_chat_graph.invoke()` → `await source_chat_graph.ainvoke()`, `asyncio.to_thread(get_state)` → `await aget_state()`
- **`open_notebook/utils/graph_utils.py`**: Thay `asyncio.to_thread(graph.get_state)` → `await graph.aget_state()`
- **`open_notebook/database/repository.py`**: Không cần thay đổi logic, chỉ đảm bảo tương thích (Pool đã đúng, chỉ cần tất cả caller dùng chung 1 event loop)
- **Dependencies**: Cần kiểm tra `langgraph` đã có `AsyncSqliteSaver` chưa, nếu không dùng `aiosqlite` adapter
