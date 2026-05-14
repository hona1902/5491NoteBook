## Why

Open Notebook hiện chỉ có bảo vệ đơn giản bằng mật khẩu toàn cục (`OPEN_NOTEBOOK_PASSWORD`) — tất cả người dùng chia sẻ cùng một token, không có khái niệm danh tính người dùng riêng biệt, không phân biệt được dữ liệu ai với ai. Khi triển khai self-hosted cho nhiều người (ví dụ nhóm nội bộ), cần hệ thống multi-user thực sự với phân quyền rõ ràng, đảm bảo mỗi user chỉ truy cập dữ liệu của họ và không có đăng ký public.

## What Changes

- **Thêm** bảng `app_user` trong SurrealDB (username, email, password_hash, role, is_active, created_at, updated_at, last_login_at).
- **Thêm** JWT-based authentication thay thế cơ chế password toàn cục hiện tại.
- **Thêm** dependency `get_current_user` và `require_admin` vào FastAPI để inject user context vào mọi request.
- **Thêm** endpoints: `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`, `POST /api/auth/change-password`.
- **Thêm** admin endpoints: `GET/POST /api/admin/users`, `PATCH/DELETE /api/admin/users/{id}`, `PATCH /api/admin/users/{id}/password`.
- **Thêm** trường `owner_id` vào các bảng `note`, `chat_session` để filter theo user.
- **Thêm** trường `created_by` vào bảng `notebook` để tracking ai tạo (admin).
- **Sửa** tất cả endpoints notes và chat để enforce `owner_id = current_user.id`.
- **Sửa** endpoints notebooks: chỉ admin POST/DELETE/PUT.
- **Thêm** trang login frontend, auth context/provider, route guard.
- **Thêm** UI admin quản lý users (thêm/sửa/xóa/đổi mật khẩu/bật-tắt).
- **Thêm** seed/bootstrap admin đầu tiên qua env vars hoặc CLI command.
- **Thêm** migration strategy cho dữ liệu cũ (gán cho default admin).
- **Xóa bỏ** cơ chế `PasswordAuthMiddleware` toàn cục sau khi JWT đầy đủ (hoặc giữ lại song song làm fallback).

## Capabilities

### New Capabilities

- `user-auth`: Hệ thống đăng nhập username/password + JWT token với expiry, không có đăng ký public. Bao gồm login, logout, me, change-password endpoints.
- `user-management`: Admin quản lý users: tạo, sửa, xóa, đổi mật khẩu, bật/tắt active. Bao gồm admin user CRUD endpoints và UI admin.
- `user-data-isolation`: Mỗi user chỉ truy cập được notes và chat sessions của chính mình (owner_id filter). IDOR protection ở backend.
- `notebook-shared-resource`: Notebooks là tài nguyên chung, chỉ admin tạo/xóa/sửa. User thường chỉ read notebooks và dùng chúng để chat/ghi notes.
- `admin-bootstrap`: Tạo admin đầu tiên qua env vars (`ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`) hoặc CLI command khi chưa có user nào trong DB.
- `auth-data-migration`: Migration strategy để gán dữ liệu cũ (notes, chat sessions, notebooks) cho default admin khi lần đầu enable auth.

### Modified Capabilities

- `sse-streaming-notebook-chat`: Chat sessions phải được filter theo `current_user.id`, không trả về sessions của tất cả users.

## Impact

**Backend:**
- `api/auth.py` — refactor từ `PasswordAuthMiddleware` sang JWT middleware + `get_current_user` dependency.
- `api/routers/auth.py` — thêm login/logout/me/change-password endpoints.
- `api/routers/notes.py` — thêm `owner_id` filter cho mọi query.
- `api/routers/chat.py` — thêm `owner_id` filter cho chat sessions và messages.
- `api/routers/notebooks.py` — enforce admin-only cho POST/PUT/DELETE.
- `api/routers/admin.py` — **file mới** cho user management endpoints.
- `api/main.py` — đăng ký admin router, sửa excluded_paths.
- `api/models.py` — thêm Pydantic models cho User, Login, AdminUserCreate, v.v.
- `open_notebook/domain/` — thêm `user.py` với `AppUser` model.
- `open_notebook/database/migrations/` — thêm migration file tạo `app_user` table và thêm `owner_id` vào `note`, `chat_session`, `created_by` vào `notebook`.

**Frontend:**
- `frontend/src/app/(auth)/login/page.tsx` — đã có route, cần implement UI login thực sự.
- `frontend/src/lib/stores/` — thêm auth store (Zustand hoặc tương tự).
- `frontend/src/components/` — thêm route guard component, auth provider.
- `frontend/src/app/(dashboard)/admin/` — **folder mới** với pages quản lý users.
- `frontend/src/lib/api/` — thêm auth API client, user management API client.
- `frontend/src/app/layout.tsx` — wrap với auth provider.

**Dependencies:**
- Backend: thêm `python-jose[cryptography]` hoặc `PyJWT`, `passlib[argon2]` hoặc `bcrypt`.
- Frontend: không cần thêm nếu dùng fetch/axios đã có + Next.js middleware.

**Database:**
- SurrealDB: thêm bảng `app_user`.
- Thêm field `owner_id` (relation tới `app_user`) vào bảng `note`, `chat_session`.
- Thêm field `created_by` vào bảng `notebook`.
- Migration script để gán dữ liệu cũ cho default admin.

**Security:**
- Password hashing: argon2id (qua `passlib[argon2]`).
- JWT: HS256, expiry 24h (configurable).
- IDOR protection: mọi query resource phải join với `owner_id = current_user.id`.
- Admin guard: decorator/dependency `require_admin` cho mọi `/api/admin/*`.
