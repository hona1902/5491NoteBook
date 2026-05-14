## Context

The app has an internal JWT auth system with two roles: `admin` and `user`. Data isolation for notebooks, notes, and chat sessions was implemented in prior changes. Three areas remain unguarded:

1. **Sources**: All endpoints currently have **no auth dependency** at all — both create/delete and list/view are unauthenticated.
2. **Manage sidebar & admin pages**: The sidebar already filters `Admin/Users` by role, but `Models` (`/settings/api-keys`), `Transformations`, `Settings`, and `Advanced` are visible to all authenticated users, and their backend routers have **no `require_admin`** dependency.
3. **Theme preferences**: Theme is stored in Zustand's `persist` middleware under `localStorage['theme-storage']`. This is browser-global — switching users on the same browser leaks the previous user's theme choice. There is no server-side per-user preference record.

Current auth infrastructure:
- `api/auth.py`: `get_current_user()` and `require_admin()` FastAPI dependencies
- `open_notebook/domain/user.py`: `AppUser` model (no preferences field)
- `frontend/src/lib/stores/auth-store.ts`: Zustand + persist; holds `user` (with `role`)
- `frontend/src/lib/stores/theme-store.ts`: Zustand + `localStorage` persist; totally separate from auth

## Goals / Non-Goals

**Goals:**
- Any authenticated user (`user` or `admin`) can read sources (list + detail).
- Only `admin` can create, update, delete sources, trigger reprocessing, or manage source-notebook assignments.
- Only `admin` can access Settings, Models (api-keys), Transformations, Advanced, Admin/Users pages — enforced at both frontend route level and backend API level.
- Regular users see only "Change Password" under the Manage sidebar section.
- Theme preference is stored per-user on the server; loaded at login; persisted via API on change; cleared on logout.
- Switching users on the same browser produces the correct theme for each user.
- Backend returns `403 Forbidden` (not just hidden UI) for all unauthorized write attempts.

**Non-Goals:**
- Admin cannot set another user's theme preference through this change (no admin override endpoint for preferences).
- No public registration flow changes.
- No notebook-level source visibility filtering (sources remain a global resource; access control is on mutation only).
- No i18n/localization changes for new UI strings (will use English inline text for now; i18n keys can be added separately).
- No change to podcast or notes permissions.

## Decisions

### D1 — Separate `user_preferences` table (not column on `app_user`)

**Decision**: Create a `user_preferences` SurrealDB record linked to `app_user` via `user_id` field rather than adding a `theme` column directly to `app_user`.

**Rationale**: Keeps `AppUser` model lean; preferences can grow (language, density, sidebar state) without repeated schema migrations on the user table. One-to-one relationship is easy to enforce with a UNIQUE index on `user_id`.

**Alternative considered**: Add `theme: Optional[str]` directly to `AppUser`. Simpler but conflates identity with preferences; harder to extend later.

### D2 — `GET/PATCH /users/me/preferences` (not `/auth/me/preferences`)

**Decision**: Namespace under `/users/me/` to be consistent with REST conventions for user-scoped resources.

**Alternative**: `/auth/me/preferences` — feels semantically off; auth namespace should handle tokens, not preference data.

### D3 — Keep `localStorage` as pre-hydration fallback only

**Decision**: The `theme-script.ts` inline script that reads `localStorage['theme-storage']` before React hydration stays — it prevents flash of wrong theme. After hydration, the preferences store syncs from the server and overwrites `localStorage` with the correct user value.

**Rationale**: Removing the pre-hydration script would cause a light→dark or dark→light flash on every page load. The script is harmless as a temporary fallback.

**Migration path for existing localStorage data**: After login, if the server returns no preference (first login after this change), read `localStorage['theme-storage']` and immediately call `PATCH /users/me/preferences` to persist it. This silently migrates the browser-local setting to the server.

### D4 — Frontend `AdminRoute` wrapper component

**Decision**: Create a `<AdminRoute>` React component that checks `user.role === 'admin'` from `useAuthStore`. If not admin, renders an `AccessDenied` page (not a redirect) so the URL stays in the address bar and the user understands why they can't access the page.

**Alternative**: Redirect to `/notebooks`. Rejected because it gives no feedback and looks like a broken link.

### D5 — Source-notebook assignment endpoints

**Decision**: Add two new endpoints:
- `POST /sources/{source_id}/notebooks/{notebook_id}` → admin only
- `DELETE /sources/{source_id}/notebooks/{notebook_id}` → admin only

These wrap the existing `source.add_to_notebook()` / remove logic that currently only exists inside the source create flow.

**Rationale**: The Source Detail page already shows a notebook checkbox UI that reads existing associations via `GET /sources/{id}` (which includes `notebooks: []`). Making assignment a discrete, guarded endpoint is cleaner than bundling it in a PATCH on the source.

### D6 — Backend guards for Settings/Models/Transformations/Advanced

**Decision**: Add `Depends(require_admin)` to the router-level or per-endpoint level in:
- `api/routers/settings.py` (both GET and PUT)
- `api/routers/models.py` (all routes)
- `api/routers/credentials.py` (all routes — already likely admin-only by intent)
- `api/routers/transformations.py` (all routes)
- `api/routers/embedding.py` + `embedding_rebuild.py` (all routes)
- `api/routers/config.py` (review; likely admin-only)

**Note**: `GET /settings` will also require admin. If in the future a user-accessible settings subset is needed, a new read-only endpoint can be added.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Users who currently rely on unauthenticated `/sources` access (e.g., scripts or direct API calls) will get 401 | Document in CHANGELOG; this is an intentional security tightening |
| Theme flash on first load (before server preference is fetched) | Pre-hydration script reads localStorage as fallback; server value applied as soon as auth store hydrates |
| `user_preferences` record may not exist for existing users | API returns default preference (`{ theme: 'system' }`) if no record found; record is created on first PATCH |
| Admin route guard is frontend-only; a determined user can still hit the API | Backend guards are the primary enforcement; frontend guard is UX only |
| Source-notebook checkboxes currently exist in `SourceDetailContent.tsx` but exact implementation needs verification | Check component before implementation; may need to pass `isAdmin` prop down |

## Migration Plan

1. **Database**: No migration needed for `app_user`. Create `user_preferences` table in SurrealDB via schema definition (or let the ORM auto-create on first write, consistent with existing pattern).
2. **Backend**: Deploy new endpoints and add `require_admin` guards atomically — no interim state where UI thinks it's guarded but API isn't.
3. **Frontend**: Deploy sidebar filtering and `AdminRoute` wrapper simultaneously with backend guard changes. Users currently on admin pages will see their page still load (they have the token) — no disruption.
4. **Theme migration**: Happens transparently on next login for each user. No explicit migration script required.
5. **Rollback**: Remove `require_admin` dependencies and new endpoints; revert sidebar filtering. Preferences table can remain harmlessly.

## Open Questions

- Does `GET /settings` need to be readable by regular users (e.g., to know the default embedding option when uploading a source)? → **Assume admin-only for now**; if needed, create a separate `/settings/public` read-only endpoint later.
- Should the Create button in the sidebar be hidden from regular users? → **Yes, hide source creation option** in the Create dropdown for non-admins; notebook creation can stay since users can read notebooks.
