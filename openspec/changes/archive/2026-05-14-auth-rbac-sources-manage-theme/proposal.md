## Why

The existing auth system (JWT + admin/user roles) successfully isolates notebooks, notes, and chat sessions per-user, but **Sources**, the **Manage sidebar**, and **theme preferences** still lack proper role enforcement. Regular users can currently trigger write operations on shared sources and access admin-only configuration pages, and theme changes are stored globally in localStorage rather than per-user on the server — causing theme bleed between users sharing the same browser.

## What Changes

- **Sources list (`GET /sources`)**: require authenticated user (any role); currently has no auth dependency.
- **Sources write operations** (`POST /sources`, `PUT /sources/{id}`, `DELETE /sources/{id}`, `POST /sources/{id}/reprocess`): restrict to **admin only**; currently unrestricted.
- **Source-notebook assignment** (`POST /sources/{id}/notebooks/{notebook_id}`, `DELETE /sources/{id}/notebooks/{notebook_id}`): new endpoints; admin only.
- **Source detail UI**: disable/hide notebook-assignment checkboxes for regular users; add admin-only tooltip.
- **Manage sidebar**: filter menu items by role — regular users see **only Change Password**; admins see all items.
- **Route guards** for `/settings`, `/settings/api-keys`, `/transformations`, `/advanced`, `/admin/users`: redirect non-admin users with an "Access Denied" page.
- **Backend guards** for all Settings, Models, Transformations, Advanced, Admin/Users APIs: add `require_admin` dependency where missing.
- **Per-user theme preference**: migrate from global localStorage to a server-side `user_preferences` table; add `GET /users/me/preferences` and `PATCH /users/me/preferences`; sync theme on login and on change; clear on logout.
- **`AppUser` domain model**: no `theme` field added directly — store preferences in a separate lightweight table/record to keep the user model lean.

## Capabilities

### New Capabilities

- `source-rbac`: Role-based guards on all source CRUD and reprocess endpoints; source-notebook assignment endpoints with admin-only enforcement.
- `manage-sidebar-rbac`: Frontend navigation filtering by role; admin-route guard component for protected pages.
- `user-preferences`: Per-user server-side preferences (theme); new domain model `UserPreferences`; API endpoints `GET/PATCH /users/me/preferences`; login-time preference load; logout cleanup.

### Modified Capabilities

- `source-notebook-assignment`: Source-to-notebook relationship mutations (add/remove) now require admin role — previously unguarded via the source create flow.
- `settings-admin-guard`: Settings, Models (api-keys), Transformations, Advanced, Admin/Users APIs now explicitly require `require_admin`; previously Settings router had no auth dependency.

## Impact

**Backend files likely affected:**
- `api/routers/sources.py` — add `get_current_user` / `require_admin` dependencies per endpoint
- `api/routers/settings.py` — add `require_admin`
- `api/routers/transformations.py` — add `require_admin`
- `api/routers/models.py` — add `require_admin`
- `api/routers/credentials.py` — add `require_admin`
- `api/routers/embedding.py` / `api/routers/embedding_rebuild.py` — add `require_admin`
- `api/routers/commands.py` — review and guard admin commands
- `api/routers/config.py` / `api/routers/advanced` routes — add `require_admin`
- `api/auth.py` — already has `get_current_user` and `require_admin`; no changes needed
- `open_notebook/domain/user.py` — no changes needed
- New file: `open_notebook/domain/user_preferences.py` — `UserPreferences` domain model
- New file: `api/routers/user_preferences.py` — preferences endpoints
- `api/main.py` — register new preferences router

**Frontend files likely affected:**
- `frontend/src/components/layout/AppSidebar.tsx` — filter Manage items by role; hide Create Source button for users (or keep if desired)
- `frontend/src/lib/stores/theme-store.ts` — remove standalone localStorage persist; delegate to preferences store
- New file: `frontend/src/lib/stores/preferences-store.ts` — per-user preferences state with API sync
- `frontend/src/lib/stores/auth-store.ts` — load preferences on login; clear on logout
- `frontend/src/lib/theme-script.ts` — keep localStorage fallback for pre-hydration flash prevention only
- `frontend/src/components/source/SourceDetailContent.tsx` — disable/hide notebook assignment checkboxes for non-admin
- `frontend/src/app/(dashboard)/sources/page.tsx` — hide Create/Delete/Edit/Reprocess actions for non-admin
- New file: `frontend/src/components/common/AdminRoute.tsx` — admin route guard wrapper
- `frontend/src/app/(dashboard)/settings/page.tsx`, `settings/api-keys`, `/transformations`, `/advanced`, `/admin/users` pages — wrap with `AdminRoute`

**Database:**
- New SurrealDB table: `user_preferences` with fields `user_id` (record link → `app_user`), `theme` (`'light' | 'dark' | 'system'`), `created_at`, `updated_at`
- Possible migration: if any global theme setting currently exists in DB, script to delete/ignore it (theme was localStorage-only, so no DB migration needed for existing data)
