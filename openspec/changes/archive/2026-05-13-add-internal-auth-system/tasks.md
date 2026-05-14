## 1. Dependencies & Configuration

- [x] 1.1 Thêm `passlib[argon2]` và `python-jose[cryptography]` vào `pyproject.toml` dependencies
- [x] 1.2 Thêm env vars `JWT_SECRET_KEY` và `JWT_ACCESS_TOKEN_EXPIRE_HOURS` vào `.env.example` và document trong `CONFIGURATION.md`
- [x] 1.3 Thêm env vars `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` vào `.env.example` với comments rõ ràng
- [x] 1.4 Chạy `uv add passlib[argon2] python-jose[cryptography]` để cập nhật `uv.lock`

## 2. Database Migration — Schema

- [x] 2.1 Tạo migration file mới trong `open_notebook/database/migrations/` (version tiếp theo sau version hiện tại) với SurrealQL tạo bảng `app_user`:
  ```sql
  DEFINE TABLE app_user SCHEMAFULL;
  DEFINE FIELD username ON app_user TYPE string ASSERT $value != NONE;
  DEFINE FIELD email ON app_user TYPE string ASSERT $value != NONE;
  DEFINE FIELD password_hash ON app_user TYPE string;
  DEFINE FIELD role ON app_user TYPE string DEFAULT "user" ASSERT $value IN ["admin", "user"];
  DEFINE FIELD is_active ON app_user TYPE bool DEFAULT true;
  DEFINE FIELD created_at ON app_user TYPE datetime DEFAULT time::now();
  DEFINE FIELD updated_at ON app_user TYPE datetime DEFAULT time::now();
  DEFINE FIELD last_login_at ON app_user TYPE option<datetime>;
  DEFINE INDEX app_user_username_idx ON app_user FIELDS username UNIQUE;
  DEFINE INDEX app_user_email_idx ON app_user FIELDS email UNIQUE;
  ```
- [x] 2.2 Trong cùng migration file, thêm field `owner_id` vào bảng `note`:
  ```sql
  DEFINE FIELD owner_id ON note TYPE option<record<app_user>>;
  DEFINE INDEX note_owner_idx ON note FIELDS owner_id;
  ```
- [x] 2.3 Trong cùng migration file, thêm field `owner_id` vào bảng `chat_session`:
  ```sql
  DEFINE FIELD owner_id ON chat_session TYPE option<record<app_user>>;
  DEFINE INDEX chat_session_owner_idx ON chat_session FIELDS owner_id;
  ```
- [x] 2.4 Trong cùng migration file, thêm field `created_by` vào bảng `notebook`:
  ```sql
  DEFINE FIELD created_by ON notebook TYPE option<record<app_user>>;
  ```
- [x] 2.5 Verify migration chạy đúng bằng cách kiểm tra `open_notebook/database/async_migrate.py` để hiểu cách đăng ký migration version mới

## 3. Domain Layer — AppUser Model

- [x] 3.1 Tạo file `open_notebook/domain/user.py` với `AppUser(ObjectModel)`:
  - Fields: `username`, `email`, `password_hash`, `role`, `is_active`, `created_at`, `updated_at`, `last_login_at`
  - `table_name = "app_user"`
  - Method `verify_password(plain_password) -> bool` dùng passlib argon2
  - Class method `get_by_username(username) -> Optional[AppUser]`
  - Class method `get_by_email(email) -> Optional[AppUser]`
  - Class method `create_user(username, email, password, role) -> AppUser` với password hashing
  - Method `set_password(new_password)` để hash và set `password_hash`
  - `_prepare_save_data()` override để exclude `password_hash` là không — password_hash cần lưu DB, nhưng phải exclude khỏi API response
- [x] 3.2 Tạo `AppUserResponse` Pydantic model (không có `password_hash`) để dùng trong API responses
- [x] 3.3 Thêm `AppUser` vào `open_notebook/domain/__init__.py` exports

## 4. Backend Auth Layer — JWT

- [x] 4.1 Refactor `api/auth.py` — thêm các functions JWT:
  - `create_access_token(data: dict) -> str` dùng `python-jose`
  - `decode_access_token(token: str) -> dict` với error handling
  - FastAPI dependency `get_current_user(token: HTTPAuthorizationCredentials) -> AppUser`
  - FastAPI dependency `require_admin(current_user: AppUser = Depends(get_current_user)) -> AppUser`
- [x] 4.2 Trong `api/auth.py`, thêm startup check: nếu `JWT_SECRET_KEY` không set, raise `RuntimeError` (được gọi trong lifespan)
- [x] 4.3 Giữ nguyên `PasswordAuthMiddleware` class nhưng không remove nó — sẽ disable sau khi verify JWT hoạt động

## 5. Backend Auth Endpoints

- [x] 5.1 Sửa `api/routers/auth.py` — thêm `POST /auth/login` endpoint:
  - Accept `LoginRequest(username_or_email: str, password: str)`
  - Lookup user bằng username hoặc email
  - Verify password với argon2
  - Check `is_active`
  - Nếu thành công: return `LoginResponse(access_token, token_type, user: AppUserResponse)`
  - Nếu thất bại: return HTTP 401 với generic message (không tiết lộ user có tồn tại hay không)
- [x] 5.2 Thêm `POST /auth/logout` endpoint (stateless — trả về 200 với message)
- [x] 5.3 Thêm `GET /auth/me` endpoint với `get_current_user` dependency
- [x] 5.4 Thêm `POST /auth/change-password` endpoint với `get_current_user` dependency:
  - Accept `ChangePasswordRequest(current_password: str, new_password: str)`
  - Verify current password
  - Hash và set new password
  - Update `last_login_at` khi login thành công (trong login endpoint)
- [x] 5.5 Cập nhật `api/models.py` — thêm Pydantic models: `LoginRequest`, `LoginResponse`, `ChangePasswordRequest`, `AppUserResponse`, `AdminCreateUserRequest`, `AdminUpdateUserRequest`

## 6. Admin User Management Endpoints

- [x] 6.1 Tạo file `api/routers/admin.py` với router prefix `/admin`
- [x] 6.2 Thêm `GET /admin/users` — list all users, dùng `require_admin` dependency
- [x] 6.3 Thêm `POST /admin/users` — create new user, admin only:
  - Validate unique username/email
  - Hash password với argon2id
  - Return `AppUserResponse` (no password_hash)
- [x] 6.4 Thêm `PATCH /admin/users/{user_id}` — update user info (username, email, role, is_active):
  - `require_admin` dependency
- [x] 6.5 Thêm `PATCH /admin/users/{user_id}/password` — admin resets user password
- [x] 6.6 Thêm `DELETE /admin/users/{user_id}`:
  - Check: nếu đây là admin duy nhất còn lại thì return HTTP 400
  - Nếu user tự xóa mình và là admin duy nhất: return HTTP 400
- [x] 6.7 Đăng ký `admin.router` trong `api/main.py` với prefix `/api`, thêm `/api/admin/*` vào excluded paths của `PasswordAuthMiddleware`

## 7. Notes Router — Owner Enforcement

- [x] 7.1 Sửa `api/routers/notes.py` — thêm `get_current_user` dependency vào mọi endpoint
- [x] 7.2 `POST` notes: gán `owner_id = current_user.id` khi tạo note
- [x] 7.3 `GET` notes (list): thêm `WHERE owner_id = $user_id` vào SurrealQL query
- [x] 7.4 `GET /notes/{note_id}`: thêm `AND owner_id = $user_id` vào query; return 404 nếu không match
- [x] 7.5 `PUT /notes/{note_id}`: verify ownership trước khi update; return 404 nếu không phải của user
- [x] 7.6 `DELETE /notes/{note_id}`: verify ownership; return 404 nếu không phải của user

## 8. Chat Router — Owner Enforcement

- [x] 8.1 Sửa `api/routers/chat.py` — thêm `get_current_user` dependency vào mọi endpoint
- [x] 8.2 `POST` chat sessions: gán `owner_id = current_user.id`
- [x] 8.3 `GET` chat sessions (list per notebook): filter `WHERE owner_id = $user_id`
- [x] 8.4 `GET /chat/{session_id}`: thêm `AND owner_id = $user_id` vào query
- [x] 8.5 `POST /chat/{session_id}/messages`: verify session ownership trước khi allow
- [x] 8.6 `DELETE /chat/{session_id}`: verify ownership
- [x] 8.7 SSE streaming chat endpoint: verify session ownership trước khi stream

## 9. Notebooks Router — Admin Guard

- [x] 9.1 Sửa `api/routers/notebooks.py`:
  - `POST /notebooks`: thêm `require_admin` dependency, set `created_by = current_user.id`
  - `PUT /notebooks/{id}`: thêm `require_admin` dependency
  - `DELETE /notebooks/{id}`: thêm `require_admin` dependency
  - `GET /notebooks` và `GET /notebooks/{id}`: thêm `get_current_user` dependency (không require admin)
- [x] 9.2 Sửa `api/main.py` — update `excluded_paths` trong `PasswordAuthMiddleware` để thêm `/api/auth/login`

## 10. Admin Bootstrap & Data Migration

- [x] 10.1 Trong `api/main.py` `lifespan()`, sau khi migration chạy, thêm:
  - Check `JWT_SECRET_KEY` (raise RuntimeError nếu không có)
  - Check if `app_user` table is empty
  - Nếu trống và env vars set: tạo admin đầu tiên
- [x] 10.2 Tạo function `bootstrap_admin(admin_user_id: str)` trong `open_notebook/domain/user.py` hoặc `api/startup.py`:
  - Update tất cả `note` records có `owner_id = null` → set `owner_id = admin_id`
  - Update tất cả `chat_session` records có `owner_id = null` → set `owner_id = admin_id`
  - Update tất cả `notebook` records có `created_by = null` → set `created_by = admin_id`
  - Log count cho từng loại
- [x] 10.3 Gọi `bootstrap_admin()` trong lifespan sau khi tạo admin đầu tiên

## 11. Frontend — Auth Store & Context

- [x] 11.1 Tạo `frontend/src/lib/stores/authStore.ts` (Zustand) với state: `user`, `token`, `isAuthenticated`; actions: `login(token, user)`, `logout()`, `setUser(user)`
- [x] 11.2 Tạo `frontend/src/lib/api/auth.ts` với API client functions: `loginApi(username, password)`, `getMeApi()`, `changePasswordApi(current, newPw)`, `logoutApi()`
- [x] 11.3 Tạo `frontend/src/lib/api/adminUsers.ts` với: `listUsersApi()`, `createUserApi()`, `updateUserApi()`, `deleteUserApi()`, `resetUserPasswordApi()`
- [x] 11.4 Tạo `frontend/src/middleware.ts` ở root của `frontend/src/`: check JWT token in localStorage/cookie, redirect unauthenticated users to `/login`
- [x] 11.5 Cập nhật `frontend/src/app/layout.tsx` — wrap app với auth initialization logic (hydrate store from localStorage on mount)

## 12. Frontend — Login Page

- [x] 12.1 Implement `frontend/src/app/(auth)/login/page.tsx` đầy đủ:
  - Form với username/email và password fields
  - Submit call `loginApi()`, store token + user vào authStore
  - Redirect về `/` sau login thành công
  - Hiển thị error message generic khi login fail
  - Hiển thị "Account is disabled" nếu nhận HTTP 403
  - Không có "Sign up" link hay bất kỳ đường dẫn đăng ký nào
- [x] 12.2 Tạo UI đẹp cho login page (loading state, error state, responsive)

## 13. Frontend — Route Guard & Admin UI

- [x] 13.1 Tạo component `frontend/src/components/auth/RouteGuard.tsx` — redirect về login nếu không authenticated
- [x] 13.2 Tạo component `frontend/src/components/auth/AdminGuard.tsx` — redirect về `/` nếu không phải admin
- [x] 13.3 Tạo `frontend/src/app/(dashboard)/admin/users/page.tsx` — trang quản lý users:
  - List users (table với username, email, role, is_active, created_at)
  - Create user button (mở modal/form)
  - Edit user (inline edit hoặc modal)
  - Delete user (confirmation dialog, disabled nếu last admin)
  - Reset password (modal)
  - Toggle active/inactive
- [x] 13.4 Ẩn "Create Notebook" button trong `frontend/src/app/(dashboard)/notebooks/` dựa trên `user.role !== "admin"`
- [x] 13.5 Tạo `frontend/src/app/(dashboard)/settings/change-password/page.tsx` — UI đổi mật khẩu cho user thường
- [x] 13.6 Thêm link "Admin" trong navigation (chỉ hiện với admin role)
- [x] 13.7 Thêm "Change Password" link vào user menu cho tất cả users

## 14. Testing

- [x] 14.1 Viết unit tests cho `api/auth.py`: `create_access_token`, `decode_access_token`, `get_current_user` dependency
- [x] 14.2 Viết unit tests cho `AppUser.verify_password()` và `AppUser.set_password()`
- [x] 14.3 Viết integration tests cho `POST /api/auth/login`: success, wrong password, inactive user, non-existent user
- [x] 14.4 Viết integration tests cho IDOR protection: user A cannot GET/PUT/DELETE note belonging to user B
- [x] 14.5 Viết integration tests cho admin guard: regular user cannot POST `/api/notebooks`, `/api/admin/users`
- [x] 14.6 Viết integration test: admin cannot delete last admin
- [x] 14.7 Viết integration test: bootstrap creates admin when `app_user` table is empty
- [x] 14.8 Viết test: `GET /api/auth/me` response never includes `password_hash`
- [x] 14.9 Viết test: `GET /api/admin/users` response never includes `password_hash`

## 15. Security Hardening & Documentation

- [x] 15.1 Verify trong mọi API response (`AppUserResponse`) không có field `password_hash`
- [x] 15.2 Đảm bảo login error message giống nhau cho "wrong password" và "user not found" (dùng constant-time comparison hay same message string)
- [x] 15.3 Thêm index SurrealDB cho `owner_id` queries (xem task 2.2, 2.3)
- [x] 15.4 Update `CONFIGURATION.md` với hướng dẫn setup auth system mới
- [x] 15.5 Update `docker-compose.yml` để thêm `JWT_SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` env vars
- [x] 15.6 Sau khi toàn bộ JWT auth hoạt động và verified, xóa hoặc disable `PasswordAuthMiddleware` trong `api/main.py`
