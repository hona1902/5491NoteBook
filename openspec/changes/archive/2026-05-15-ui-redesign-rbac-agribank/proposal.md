## Why

The open-notebook frontend currently uses a default blue-themed shadcn/ui design system that doesn't reflect the Agribank brand identity (`#AE1C3F` deep red). Additionally, while backend RBAC guards exist, the frontend UI lacks consistent role-aware behavior: standard users still see admin-only action buttons (delete, reprocess, source assignment checkboxes), navigation items are conditionally hidden but not comprehensively enforced, and there is no Access Denied page for direct URL access to restricted routes. The Change Password form renders inline alongside the sidebar instead of as a modal dialog, and theme preferences—while synced to the server—still use a global `localStorage` key that can leak between users on shared devices. These issues create a fragmented, confusing experience that must be unified before the app goes to production.

## What Changes

- **Brand color migration**: Replace the default blue primary color (`oklch(0.623 0.214 259.815)`) with Agribank deep red `#AE1C3F` across all CSS custom properties (`--primary`, `--ring`, `--sidebar-primary`, `--sidebar-ring`) in both light and dark themes. Derive a complementary dark-theme variant. Audit and replace ~15 instances of hard-coded `text-blue-*`, `bg-blue-*`, `border-blue-*` Tailwind classes with semantic tokens.
- **Danger/destructive color differentiation**: Since the new primary is a deep red, the existing `--destructive` red must be shifted to a distinct orange-red or bright red to avoid confusion. Add explicit icon + text labels on all destructive actions. Add confirm dialogs for all destructive operations.
- **Role-based sidebar navigation**: Refine `AppSidebar.tsx` `getNavigation()` to cleanly separate admin-only and shared items. Hide the "Create" dropdown for non-admin users (or limit to allowed create targets). Show user display name and role badge in sidebar footer.
- **Role-based UI guards on Sources**: Hide delete button, upload/reprocess actions for non-admin users on `SourcesPage`. Disable notebook-assignment checkboxes in `SourceDetailContent.tsx` with a hint tooltip for non-admins. Hide source creation wizards for non-admins.
- **Role-based UI guards on Notebooks**: Hide create/edit/delete notebook buttons for non-admin users. Show a "Shared by admin" badge on notebooks. Allow non-admins to interact with chat/notes within notebooks.
- **Notes/Chat ownership clarity**: Add "Your Notes" / "Your Chat" header labels. Ensure no cross-user data is displayed or implied.
- **Admin Users management page**: Polish the existing `/admin/users` page with proper data table, confirm dialogs, self-deletion protection, and empty/loading/error states.
- **Change Password as modal dialog**: Replace the current inline `/settings/change-password` page with a modal/dialog triggered from sidebar, with validation and success feedback.
- **Access Denied page**: Create a dedicated, readable Access Denied component for unauthorized direct URL access (replacing the current silent redirect in `AdminGuard.tsx`).
- **Theme per-user isolation**: Namespace `localStorage` theme key with user ID. Clear user-specific UI state on logout. Ensure server preference is always synced after login.
- **Visual polish**: Consistent loading spinners, empty states, error states across all pages. Smooth transitions. Responsive layout refinements for tablet.

## Capabilities

### New Capabilities
- `brand-color-system`: Design token migration from blue to Agribank `#AE1C3F`, including light/dark theme variants, contrast validation, danger color differentiation, and hard-coded color audit.
- `rbac-ui-guards`: Comprehensive role-based UI visibility and interaction controls across sidebar, sources, notebooks, notes/chat, admin, and direct URL access denial.
- `change-password-dialog`: Modal-based password change flow replacing the current inline page, with validation and success feedback.
- `access-denied-page`: Standalone Access Denied component for unauthorized route access with clear messaging and navigation.

### Modified Capabilities
- `user-preferences`: Theme localStorage key must be namespaced per-user and cleared on logout to prevent cross-user leakage.
- `manage-sidebar-rbac`: Sidebar navigation must also conditionally show/hide the "Create" dropdown items and display user identity/role.
- `source-rbac`: Frontend must enforce read-only UI for non-admin users on source detail pages (checkboxes, action buttons).
- `user-management`: Admin Users page needs polish with data table, confirm dialogs, and self-deletion safeguards.

## Impact

- **CSS/Theme files**: `frontend/src/app/globals.css` (all CSS custom properties), `frontend/tailwind.config.ts`
- **Sidebar**: `frontend/src/components/layout/AppSidebar.tsx`
- **Auth components**: `frontend/src/components/auth/AdminGuard.tsx`, `AdminRoute.tsx`
- **Sources pages/components**: `frontend/src/app/(dashboard)/sources/page.tsx`, `frontend/src/components/source/SourceDetailContent.tsx`, `frontend/src/components/source/NotebookAssociations.tsx`, `frontend/src/components/sources/SourceCard.tsx`, `frontend/src/components/sources/AddSourceDialog.tsx`
- **Notebooks pages**: `frontend/src/app/(dashboard)/notebooks/page.tsx`, `frontend/src/components/notebooks/CreateNotebookDialog.tsx`
- **Admin Users**: `frontend/src/app/(dashboard)/admin/users/page.tsx`
- **Settings/Change Password**: `frontend/src/app/(dashboard)/settings/change-password/page.tsx`
- **Stores**: `frontend/src/lib/stores/theme-store.ts`, `frontend/src/lib/stores/preferences-store.ts`, `frontend/src/lib/stores/auth-store.ts`
- **Common components**: `frontend/src/components/common/EmptyState.tsx`, `LoadingSpinner.tsx`, `ThemeToggle.tsx`
- **UI primitives**: `frontend/src/components/ui/button.tsx`, `badge.tsx` (if color tokens change)
- **No backend changes required** — all guards already exist server-side. This is purely a frontend UI change.
