## Context

Open Notebook là ứng dụng self-hosted với backend FastAPI, frontend Next.js, database SurrealDB. Cơ chế auth hiện tại là `PasswordAuthMiddleware` — một shared password toàn cục trong env var `OPEN_NOTEBOOK_PASSWORD`. Không có khái niệm user identity, không phân biệt data giữa các users, không có phân quyền.

**Yêu cầu cốt lõi**: Thêm hệ thống auth multi-user thực sự, không có đăng ký public, chỉ admin tạo user. Phải không phá vỡ flow hiện tại của notebooks/notes/chat.

**Constraints quan trọng**:
- SurrealDB không có built-in password hashing, phải xử lý ở tầng application.
- Migration dữ liệu cũ (notes, chat, notebooks không có `owner_id`) phải được xử lý khi lần đầu bootstrap.
- Cơ sở hạ tầng async graph execution (custom) phải vẫn hoạt động.
- Frontend đã có route group `(auth)/login/` — cần implement thực sự.

## Goals / Non-Goals

**Goals:**
- Thay thế password middleware toàn cục bằng JWT-based user authentication.
- Thêm `AppUser` model với roles (admin/user), password hash (argon2), is_active.
- Enforce data isolation: notes và chat sessions chỉ trả về records của `current_user`.
- Admin-only: tạo/sửa/xóa notebooks, CRUD user management.
- Bootstrap admin đầu tiên an toàn qua env vars (không mở public registration).
- Migration dữ liệu cũ: gán cho default admin.
- Frontend: login page, auth context, route guard, admin UI.

**Non-Goals:**
- OAuth2 / SSO / social login (không trong scope này).
- Phân quyền granular (e.g., per-notebook permission cho từng user — scope tương lai).
- Public registration endpoint bất kỳ hình thức nào.
- Rate limiting / brute-force protection (được recommend nhưng không là blocking requirement).
- Email verification / password reset qua email.
- Shared notebooks giữa 2 user thường (notebooks là global shared resource của admin).

## Decisions

### Decision 1: JWT (HS256) thay vì Session-based auth

**Chọn**: JWT access token với expiry 24h, không refresh token trong phase đầu.

**Lý do**: 
- FastAPI ecosystem tự nhiên với JWT. 
- Stateless — không cần session store thêm.
- Frontend Next.js dễ dàng lưu token vào `localStorage` hoặc cookie HttpOnly.

**Thay thế đã cân nhắc**: 
- Session cookie với server-side session store trong SurrealDB → phức tạp hơn, cần thêm bảng session, không cần thiết cho self-hosted.
- Refresh token → thêm complexity; có thể bổ sung sau.

**Token storage ở frontend**: `localStorage` cho đơn giản (self-hosted, low XSS risk); chú thích trong code để chuyển sang HttpOnly cookie nếu muốn hardened security.

---

### Decision 2: Argon2id cho password hashing

**Chọn**: `passlib[argon2]` với `CryptContext(schemes=["argon2"])`.

**Lý do**: Argon2id là OWASP recommended winner. Chống GPU brute-force tốt hơn bcrypt. Python library passlib hỗ trợ tốt.

**Thay thế**: bcrypt (cũng tốt, nếu không cài được argon2-cffi thì fallback bcrypt).

---

### Decision 3: `app_user` là bảng riêng trong SurrealDB (không dùng SurrealDB native user/scope)

**Chọn**: Tạo bảng `app_user` như một ObjectModel thông thường.

**Lý do**: 
- SurrealDB native users/scopes có API riêng, phức tạp và ít documented hơn.
- Consistent với codebase hiện tại (mọi domain object đều là ObjectModel).
- Dễ migration, dễ test, dễ backup.

**Rủi ro**: Phải tự quản lý security (password không được lộ qua API), cần `model_dump(exclude={'password_hash'})` ở mọi response serializer.

---

### Decision 4: `owner_id` là string field (SurrealDB RecordID dưới dạng string)

**Chọn**: Thêm field `owner_id: Optional[str]` vào `Note` và `ChatSession`, lưu dạng `"app_user:xxx"`.

**Lý do**: Consistent với cách codebase hiện tại handle RecordID (xem `Source.command` field — dùng string). Tránh complexity của typed RecordID trong Pydantic.

**Nullable**: `Optional` để backward-compatible với dữ liệu cũ (sẽ được gán cho admin trong migration).

---

### Decision 5: Giữ lại `PasswordAuthMiddleware` song song trong giai đoạn transition

**Chọn**: Khi JWT auth đã hoạt động, middleware cũ bị bypass (nếu `OPEN_NOTEBOOK_PASSWORD` không set, middleware không chặn gì). Sau khi verify đầy đủ, xóa middleware hoặc disable.

**Lý do**: An toàn hơn là xóa ngay, tránh mất access nếu JWT có bug.

---

### Decision 6: Admin bootstrap qua env vars + lifespan event

**Chọn**: Trong `lifespan()` của FastAPI, sau migration, kiểm tra `app_user` table có record nào không. Nếu trống, đọc `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` từ env và tạo admin đầu tiên.

**Lý do**: Không cần CLI riêng. Tự động trong startup. An toàn — chỉ tạo khi table trống.

**Alternative**: CLI command `python -m open_notebook.cli create-admin` — có thể bổ sung sau.

---

### Decision 7: Frontend auth với Next.js middleware + Zustand store

**Chọn**: 
- `middleware.ts` ở root để check token và redirect nếu unauthenticated.
- Zustand store (`useAuthStore`) lưu user info + token.
- Custom hook `useRequireAdmin()` cho admin routes.

**Lý do**: Next.js middleware chạy ở edge, redirect trước khi render. Zustand đã có trong project (kiểm tra `frontend/src/lib/stores/`).

## Risks / Trade-offs

**Risk 1: Data migration — notes/chat cũ không có `owner_id`** → Mitigation: Migration script tự động gán `owner_id = admin_user.id` cho tất cả records cũ. Có thể dry-run trước.

**Risk 2: IDOR — user đoán được ID của resource của user khác** → Mitigation: Mọi query `SELECT * FROM note WHERE id=$id` phải thêm `AND owner_id=$current_user_id`. Có test case cho IDOR.

**Risk 3: Admin tự xóa mình** → Mitigation: Endpoint `DELETE /api/admin/users/{id}` kiểm tra nếu đây là admin duy nhất còn lại, return 400.

**Risk 4: JWT secret không set hoặc yếu** → Mitigation: Startup check — nếu `JWT_SECRET_KEY` không set, raise RuntimeError và không start. Dùng `OPEN_NOTEBOOK_ENCRYPTION_KEY` hiện có hoặc yêu cầu env var mới.

**Risk 5: Async graph execution (custom) không biết về user context** → Mitigation: Graphs chạy background jobs, không cần user auth. Commands được submit với `source_id`/`note_id` — không thay đổi. Owner được enforce ở API layer, không ở graph layer.

**Risk 6: Chat sessions có thể relate tới notebook qua `refers_to` relation** → Mitigation: Chat session query phải `WHERE owner_id = $user_id`. Relation `refers_to` không thay đổi — chỉ filter ở session level, không ở notebook level.

**Risk 7: password_hash bị lộ trong API response** → Mitigation: `AppUser` response model (`AppUserResponse`) không bao giờ include `password_hash`. Unit test đảm bảo.

## Migration Plan

### Phase 1: Database Schema Migration
1. Thêm migration file mới (sau version hiện tại) trong `open_notebook/database/migrations/`.
2. Migration tạo bảng `app_user` với các fields cần thiết.
3. Migration thêm field `owner_id` vào `note` và `chat_session` (nullable).
4. Migration thêm field `created_by` vào `notebook` (nullable).

### Phase 2: Bootstrap & Data Migration
5. Trong `lifespan()`: nếu `app_user` table trống, tạo admin từ env vars.
6. Chạy migration script gán `owner_id = admin_id` cho tất cả notes và chat sessions cũ.
7. Gán `created_by = admin_id` cho tất cả notebooks cũ.

### Phase 3: API Layer
8. Implement `get_current_user` FastAPI dependency.
9. Implement `require_admin` dependency.
10. Implement auth endpoints.
11. Implement admin user management endpoints.
12. Sửa notes/chat routers để enforce `owner_id`.
13. Sửa notebooks router để enforce admin-only creation.

### Phase 4: Frontend
14. Implement login page UI đầy đủ.
15. Implement auth store + middleware.
16. Implement route guard.
17. Implement admin user management UI.
18. Ẩn "Create Notebook" button với user thường.

### Rollback Strategy
- Nếu JWT auth có vấn đề: set lại `OPEN_NOTEBOOK_PASSWORD` để fallback về middleware cũ (vẫn còn trong code).
- Migration DB: SurrealDB không có transaction DDL rollback — cần backup trước khi migrate.
- Frontend: revert commit, redeploy.

## Open Questions

1. **Token storage**: `localStorage` hay HttpOnly cookie? — Quyết định: localStorage cho đơn giản (có thể chuyển sau).
2. **Access token expiry**: 24h hay 8h? — Quyết định: 24h, configurable qua `JWT_ACCESS_TOKEN_EXPIRE_HOURS`.
3. **Sources có cần `owner_id` không?** — Sources trong thiết kế này là global resource (gắn với notebooks, notebooks là shared). Quyết định: Sources không cần `owner_id`, chỉ notes và chat sessions.
4. **SurrealDB index cho `owner_id` queries** — Nên thêm index `DEFINE INDEX note_owner_idx ON note FIELDS owner_id` để performance.
5. **Admin có thể xem notes/chat của user khác không?** — Quyết định: Không trong MVP này (admin quản lý users, không spy dữ liệu). Có thể mở endpoint admin riêng sau.
