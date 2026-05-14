# Fix VPS Performance Issues

## Problem Statement

Ứng dụng Open Notebook chạy trên VPS `160.30.113.168` (domain `sotay5491.io.vn`) gặp 3 vấn đề nghiêm trọng về hiệu suất khi xử lý concurrent chat requests:

1. **Cloudflare 524 Timeout** - AI response mất >100s → Cloudflare ngắt kết nối
2. **Thread Pool Exhaustion** - Backend Python không biết client đã ngắt → zombie threads chiếm hết thread pool (~40 threads) → server đóng băng hoàn toàn
3. **SurrealDB Handshake Timeout** - Mỗi request tạo mới connection tới SurrealDB → concurrent requests gây nghẽn handshake

## Scope

### Affected Components
- `api/routers/chat.py` — Notebook chat endpoint (synchronous, blocking)
- `open_notebook/graphs/chat.py` — LangGraph chat graph (sync `.invoke()`)
- `open_notebook/database/repository.py` — DB connection (no pooling)
- `frontend/src/lib/api/chat.ts` — Frontend chat API (no streaming support)
- `frontend/src/lib/hooks/useNotebookChat.ts` — Chat hook (synchronous send)

### Not Affected
- Source Chat (`source_chat.py`) — Already uses SSE streaming
- Search/Ask (`search.py`) — Already uses `.astream()` with SSE

## Motivation

Hiện tại, notebook chat là tính năng chính bị ảnh hưởng. Source chat và Ask đã được triển khai streaming, nhưng notebook chat vẫn dùng mô hình synchronous blocking. Khi 2-3 người dùng chat đồng thời, toàn bộ server bị treo trong vài phút.

Thay đổi này sẽ:
- Loại bỏ hoàn toàn lỗi Cloudflare 524 cho notebook chat
- Ngăn chặn zombie threads bằng cách detect client disconnect
- Giảm thiểu lỗi DB handshake timeout bằng connection pooling
- Mang lại trải nghiệm chat mượt mà hơn với streaming response

## Related Specs
<!-- Use existing spec names from openspec/specs/. Leave empty if none match. -->

## References
- [vps_error_analysis.md](../../vps_error_analysis.md) — Chi tiết phân tích 3 lỗi chính
- `api/routers/source_chat.py` — Mẫu SSE streaming đã hoạt động tốt
- `api/routers/search.py` — Mẫu `.astream()` đã hoạt động tốt
