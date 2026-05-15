## 1. Brand Color System — Design Token Migration

- [x] 1.1 Convert `#AE1C3F` to oklch and update `:root` in `globals.css`: replace `--primary`, `--primary-foreground`, `--ring`, `--sidebar-primary`, `--sidebar-primary-foreground`, `--sidebar-ring` for light theme
- [x] 1.2 Derive dark theme variant of `#AE1C3F` (lighter, higher luminance) and update `.dark` block in `globals.css` for the same properties
- [x] 1.3 Update `--destructive` token to orange-red (`oklch(0.60 0.22 35)` light / `oklch(0.70 0.19 35)` dark) to differentiate from new primary
- [x] 1.4 Verify contrast ratios: primary on white (≥4.5:1), white on primary (≥4.5:1), destructive on white (≥4.5:1), dark variants on dark bg (≥4.5:1)
- [x] 1.5 Replace hard-coded `text-blue-*` classes in `SourceCard.tsx` with semantic tokens (`text-primary`, `bg-primary/10`, etc.)
- [x] 1.6 Replace hard-coded `text-blue-*` classes in `SourceDetailContent.tsx` with semantic tokens
- [x] 1.7 Replace hard-coded `text-blue-*` classes in `ChatPanel.tsx` with semantic tokens (`prose-a:text-primary`)
- [x] 1.8 Replace hard-coded `text-blue-*` classes in `SourceTypeStep.tsx` with semantic tokens
- [x] 1.9 Replace hard-coded `text-blue-*` classes in `api-keys/page.tsx` with semantic tokens
- [x] 1.10 Replace hard-coded `text-blue-500` in `RebuildEmbeddings.tsx` with `text-primary`
- [x] 1.11 Run final grep for `blue-` in `src/` to confirm zero remaining hard-coded blue classes

## 2. useIsAdmin Hook

- [x] 2.1 Create `frontend/src/lib/hooks/use-is-admin.ts` with `useIsAdmin()` hook that reads `useAuthStore` and returns boolean
- [ ] 2.2 Add unit test for `useIsAdmin()` in `frontend/src/lib/hooks/use-is-admin.test.ts` *(blocked: Jest config missing ts-jest/SWC transforms)*

## 3. Sidebar RBAC — Create Dropdown & User Identity

- [x] 3.1 Update `AppSidebar.tsx`: conditionally render Create dropdown only for admin users (hide entire button for non-admin)
- [x] 3.2 Update `AppSidebar.tsx`: add user display name and role badge in sidebar footer (above sign-out button)
- [x] 3.3 Update `AppSidebar.tsx`: Change Password item triggers dialog state instead of navigation (use `onClick` handler with state/callback instead of `<Link>`)
- [ ] 3.4 Update `AppSidebar.test.tsx` to verify non-admin sidebar rendering *(blocked: Jest config)*

## 4. Access Denied Component

- [x] 4.1 Create `frontend/src/components/common/AccessDenied.tsx` with shield icon, heading, explanation text, and "Go to Notebooks" button
- [x] 4.2 Update `AdminGuard.tsx` to render `<AccessDenied />` instead of `<LoadingSpinner />` and remove `router.push('/notebooks')` redirect
- [x] 4.3 Verify `AdminRoute.tsx` already shows inline Access Denied (confirm it uses semantic tokens and is accessible)

## 5. Sources Page RBAC

- [x] 5.1 Update `sources/page.tsx`: conditionally render Actions column header and delete button only for admin users
- [x] 5.2 Update `sources/page.tsx`: hide ConfirmDialog trigger for non-admin users
- [x] 5.3 Update `SourceDetailContent.tsx`: hide reprocess/delete/edit action buttons for non-admin users
- [x] 5.4 Update `NotebookAssociations.tsx`: render checkboxes as disabled for non-admin with hint text "Only admins can assign sources to notebooks"
- [x] 5.5 Update `AddSourceDialog.tsx` / `AddSourceButton.tsx`: ensure source creation is not accessible to non-admin (hidden from UI)

## 6. Notebooks Page RBAC

- [x] 6.1 Update `notebooks/page.tsx`: hide create/edit/delete notebook buttons for non-admin users
- [x] 6.2 Add admin-only dropdown on notebook cards (archive/delete hidden for non-admin)
- [x] 6.3 NotebookHeader: disable InlineEdit for non-admin, hide archive/delete buttons

## 7. Notes & Chat Ownership Labels

- [x] 7.1 Add "Your Notes" label/header in the notes panel within notebook detail
- [x] 7.2 Add "Your Chat" label/header in the chat panel within notebook detail and source detail
- [x] 7.3 Verify no cross-user data is displayed for non-admin users

## 8. Change Password Dialog

- [x] 8.1 Create `frontend/src/components/auth/ChangePasswordDialog.tsx` with Radix Dialog, react-hook-form, and Zod validation
- [x] 8.2 Implement form fields: current password, new password, confirm password with client-side validation (match check, empty check)
- [x] 8.3 Implement API call to change password endpoint with success toast and dialog close
- [x] 8.4 Implement error handling: inline error for wrong current password, network errors
- [x] 8.5 Wire sidebar "Change Password" item to open `ChangePasswordDialog`
- [x] 8.6 Redirect legacy `/settings/change-password` route to `/notebooks`

## 9. Admin Users Page Polish

- [x] 9.1 Polished `admin/users/page.tsx` with proper data table (Username, Email, Role, Status, Last Login, Actions)
- [x] 9.2 ConfirmDialog for user deletion with self-deletion protection
- [x] 9.3 ConfirmDialog for user deactivation/activation
- [x] 9.4 Proper loading (LoadingSpinner), error (AlertCircle + retry), and empty (EmptyState) states
- [x] 9.5 Page wrapped in `AdminGuard`

## 10. Theme Per-User Isolation

- [x] 10.1 Updated `theme-store.ts` with `bindToUser(userId)` and `unbindUser()` — saves themes under `theme-storage-${userId}` localStorage keys
- [x] 10.2 Auth store logout calls `unbindUser()` to reset theme to system default
- [x] 10.3 Auth store login calls `bindToUser(userId)` after preferences sync to load user-specific theme
- [x] 10.4 Test multi-user scenario: login as user A (dark), logout, login as user B (light), verify isolation — verified via browser walkthrough (admin→nam user transition, theme toggle working independently)

## 11. Visual Polish & Consistency

- [x] 11.1 Reviewed `EmptyState.tsx`: consistent styling (semantic tokens, centered layout, action slot)
- [x] 11.2 Reviewed `LoadingSpinner.tsx`: consistent sm/md/lg sizing with Loader2 icon
- [x] 11.3 Replaced `text-red-*` with `text-destructive` in SourceCard, TransformationCard, NotesColumn, NotebookCard, NotebookHeader
- [x] 11.4 Added `transition-colors duration-150` to sidebar nav buttons for smooth active state changes
- [x] 11.5 Verify responsive behavior on tablet-width viewports (768px–1024px) — verified: sidebar remains visible, layout adapts properly, no overlapping elements

## 12. Accessibility Audit

- [x] 12.1 Verified: Radix UI Checkbox/Button handle `aria-disabled` natively when `disabled` prop is set
- [x] 12.2 Verified: ChangePasswordDialog and admin users forms use `<Label htmlFor>` with matching `id` attributes
- [x] 12.3 Verified: ChangePasswordDialog uses Radix Dialog with built-in focus trapping and keyboard navigation
- [x] 12.4 Verified: AccessDenied has `role="alert"`, `aria-hidden` on icon, proper `<h1>` heading, descriptive button labels
- [x] 12.5 Verify `#AE1C3F` contrast on white meets WCAG AA — calculated: 6.91:1 (PASS AA, requires ≥4.5:1)
- [x] 12.6 Verify destructive color contrast in both themes — light: 4.63:1 PASS AA, dark: 5.35:1 PASS AA

## 13. Final Verification

- [x] 13.1 Full walkthrough as admin: all pages, all actions, theme toggle, change password — verified via browser walkthrough
- [x] 13.2 Full walkthrough as non-admin: verify hidden/disabled elements, Access Denied on admin URLs — verified: sidebar restricted, no create/delete buttons, Access Denied on /admin/users
- [x] 13.3 Build verification: TypeScript compilation and Next.js build pass successfully. Jest tests have pre-existing config issue (missing ts-jest transforms).
- [x] 13.4 Visual review: primary buttons, sidebar active state, badges, links, focus rings all use Agribank color — confirmed via screenshots
- [x] 13.5 Visual review: destructive buttons are visually distinct from primary — confirmed: orange-red trash icons vs maroon primary buttons
