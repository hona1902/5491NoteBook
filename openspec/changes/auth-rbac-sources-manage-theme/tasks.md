## 1. Backend — User Preferences Domain & API

- [ ] 1.1 Create `open_notebook/domain/user_preferences.py` with `UserPreferences` model (`user_id`, `theme`, `created_at`, `updated_at`) extending `ObjectModel`
- [ ] 1.2 Add class method `UserPreferences.get_for_user(user_id)` — returns record or `None`
- [ ] 1.3 Add class method `UserPreferences.get_or_default(user_id)` — returns record or `UserPreferences(theme='system')` without saving
- [ ] 1.4 Create `api/routers/user_preferences.py` with `GET /users/me/preferences` requiring `get_current_user`
- [ ] 1.5 Add `PATCH /users/me/preferences` endpoint — validates `theme` ∈ `{'light','dark','system'}`; upserts record; returns updated preference
- [ ] 1.6 Register `user_preferences` router in `api/main.py` under `/api` prefix
- [ ] 1.7 Add `UserPreferencesResponse` and `UserPreferencesUpdate` Pydantic models in `api/models.py`

## 2. Backend — Source RBAC Guards

- [ ] 2.1 Add `Depends(get_current_user)` to `GET /sources` in `api/routers/sources.py`
- [ ] 2.2 Add `Depends(get_current_user)` to `GET /sources/{id}` in `api/routers/sources.py`
- [ ] 2.3 Add `Depends(require_admin)` to `POST /sources` in `api/routers/sources.py`
- [ ] 2.4 Add `Depends(require_admin)` to `POST /sources/json` in `api/routers/sources.py`
- [ ] 2.5 Add `Depends(require_admin)` to `PUT /sources/{id}` in `api/routers/sources.py`
- [ ] 2.6 Add `Depends(require_admin)` to `DELETE /sources/{id}` in `api/routers/sources.py`
- [ ] 2.7 Add `Depends(require_admin)` to source status/reprocess endpoints in `api/routers/sources.py`
- [ ] 2.8 Add new endpoint `POST /sources/{source_id}/notebooks/{notebook_id}` with `require_admin` — calls `source.add_to_notebook(notebook_id)`
- [ ] 2.9 Add new endpoint `DELETE /sources/{source_id}/notebooks/{notebook_id}` with `require_admin` — removes reference relationship from SurrealDB

## 3. Backend — Admin Guards on Settings/Models/Transformations/Advanced

- [ ] 3.1 Add `Depends(require_admin)` to `GET /settings` and `PUT /settings` in `api/routers/settings.py`
- [ ] 3.2 Add router-level `dependencies=[Depends(require_admin)]` to `api/routers/transformations.py`
- [ ] 3.3 Add router-level `dependencies=[Depends(require_admin)]` to `api/routers/models.py`
- [ ] 3.4 Add router-level `dependencies=[Depends(require_admin)]` to `api/routers/credentials.py`
- [ ] 3.5 Add router-level `dependencies=[Depends(require_admin)]` to `api/routers/embedding.py`
- [ ] 3.6 Add router-level `dependencies=[Depends(require_admin)]` to `api/routers/embedding_rebuild.py`
- [ ] 3.7 Review `api/routers/config.py` and `api/routers/commands.py` — add `require_admin` to any admin-only operations

## 4. Frontend — Per-User Preferences Store

- [ ] 4.1 Create `frontend/src/lib/stores/preferences-store.ts` with Zustand store: `theme`, `loadPreferences(token)`, `updateTheme(theme, token)`, `clearPreferences()`
- [ ] 4.2 `loadPreferences` calls `GET /users/me/preferences`, sets theme in store and applies to document; calls `updateTheme` if localStorage has a non-default value (migration)
- [ ] 4.3 `updateTheme` calls `PATCH /users/me/preferences`, applies theme to document optimistically
- [ ] 4.4 `clearPreferences` resets theme to `'system'`, clears `localStorage['theme-storage']`
- [ ] 4.5 Update `auth-store.ts` login flow to call `preferencesStore.loadPreferences(token)` after successful login
- [ ] 4.6 Update `auth-store.ts` logout to call `preferencesStore.clearPreferences()`
- [ ] 4.7 Update `frontend/src/lib/stores/theme-store.ts` — remove `persist` middleware; delegate `setTheme` to call `preferencesStore.updateTheme`
- [ ] 4.8 Keep `frontend/src/lib/theme-script.ts` unchanged — still reads `localStorage` as pre-hydration fallback

## 5. Frontend — Manage Sidebar RBAC

- [ ] 5.1 Update `getNavigation()` in `AppSidebar.tsx` — filter Manage items: if `!isAdmin`, include only `changePassword` item
- [ ] 5.2 Update the Create dropdown in `AppSidebar.tsx` — hide "Source" `DropdownMenuItem` when `!isAdmin`
- [ ] 5.3 Verify sidebar test `AppSidebar.test.tsx` — add/update tests for user role showing only Change Password in Manage and admin showing full menu

## 6. Frontend — Admin Route Guard Component

- [ ] 6.1 Create `frontend/src/components/common/AdminRoute.tsx` — reads `user` from `useAuthStore`; renders children if `user?.role === 'admin'`; renders `<AccessDeniedPage />` if not
- [ ] 6.2 Create `frontend/src/components/errors/AccessDenied.tsx` — simple page with heading "Access Denied", message "You need admin privileges to access this page", and a "Go to Notebooks" link
- [ ] 6.3 Wrap `/settings/page.tsx` content with `<AdminRoute>`
- [ ] 6.4 Wrap `/settings/api-keys/page.tsx` content with `<AdminRoute>` (or directory layout if it exists)
- [ ] 6.5 Wrap `/transformations/page.tsx` content with `<AdminRoute>`
- [ ] 6.6 Wrap `/advanced/page.tsx` content with `<AdminRoute>`
- [ ] 6.7 Wrap `/admin/users/page.tsx` content with `<AdminRoute>` (currently already admin-guarded; verify consistency)

## 7. Frontend — Source List & Detail UI

- [ ] 7.1 Update `frontend/src/app/(dashboard)/sources/page.tsx` — read `isAdmin` from `useAuthStore`; conditionally render Delete/Edit/Reprocess action buttons
- [ ] 7.2 Locate source detail notebook assignment UI in `frontend/src/components/source/SourceDetailContent.tsx` — identify the checkbox/assignment component
- [ ] 7.3 Pass `isAdmin` prop (or read from store directly) into the notebook assignment section of `SourceDetailContent`
- [ ] 7.4 Disable or hide notebook assignment checkboxes when `!isAdmin`; add tooltip/caption: "Only admins can assign sources to notebooks"
- [ ] 7.5 Wire notebook assignment checkbox changes (when admin) to call `POST /sources/{id}/notebooks/{notebook_id}` or `DELETE /sources/{id}/notebooks/{notebook_id}` (new endpoints from task 2.8/2.9)

## 8. Testing

- [ ] 8.1 Add backend test: `user` role `GET /sources` → `200`
- [ ] 8.2 Add backend test: `user` role `GET /sources/{id}` → `200`
- [ ] 8.3 Add backend test: `user` role `DELETE /sources/{id}` → `403`
- [ ] 8.4 Add backend test: `user` role `POST /sources` → `403`
- [ ] 8.5 Add backend test: `user` role `POST /sources/{id}/notebooks/{notebook_id}` → `403`
- [ ] 8.6 Add backend test: `admin` role `POST /sources/{id}/notebooks/{notebook_id}` → `200`
- [ ] 8.7 Add backend test: `user` role `GET /settings` → `403`
- [ ] 8.8 Add backend test: `user` role `GET /transformations` → `403`
- [ ] 8.9 Add backend test: `user` role `GET /users/me/preferences` → `200` with default
- [ ] 8.10 Add backend test: `user` A `PATCH /users/me/preferences { theme: dark }` → user B's preference unchanged
- [ ] 8.11 Add frontend test: sidebar renders only "Change Password" in Manage for `user` role
- [ ] 8.12 Add frontend test: sidebar renders full Manage menu for `admin` role
- [ ] 8.13 Add frontend test: `AdminRoute` renders Access Denied for `user` role
- [ ] 8.14 Add frontend test: source detail notebook checkboxes are disabled for `user` role
- [ ] 8.15 Add frontend test: login for user A (dark theme) → logout → login for user B (light theme) → light theme applied
