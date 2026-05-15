## Context

Open-notebook is a Next.js 16 + React 19 application using shadcn/ui (new-york style) with Tailwind CSS v4, Zustand for state management, and Radix UI primitives. The frontend communicates with a Python/FastAPI backend via REST APIs. Authentication uses JWT tokens stored in Zustand with `persist` middleware (localStorage).

**Current state:**
- Theme system uses CSS custom properties in `globals.css` with oklch color values. Primary color is blue (`oklch(0.623 0.214 259.815)`).
- RBAC exists partially: sidebar navigation hides admin items for non-admins, `AdminGuard` redirects non-admins, `AdminRoute` shows Access Denied inline.
- Sources page shows delete buttons to all users. Source detail has notebook-assignment checkboxes without role checks.
- Change Password is a full page at `/settings/change-password`.
- Theme preference is stored in localStorage under key `theme-storage` (global, not per-user) and synced to server via `preferences-store.ts`.
- ~15 instances of hard-coded `text-blue-*`, `bg-blue-*` Tailwind classes exist across components.

**Constraints:**
- No backend API changes needed (all RBAC guards exist server-side).
- Must maintain backward compatibility with existing user workflows.
- Must work with Tailwind CSS v4 (`@theme inline` directive, not v3 `theme.extend`).
- Must work with shadcn/ui CSS variable system.

## Goals / Non-Goals

**Goals:**
- Migrate primary brand color to Agribank `#AE1C3F` with proper oklch conversion and contrast validation.
- Create a clear separation between `--primary` (brand) and `--destructive` (danger) colors.
- Enforce consistent RBAC-driven UI: hide/disable actions non-admins cannot perform.
- Provide a clear Access Denied page for unauthorized direct URL access.
- Convert Change Password from page to modal dialog.
- Isolate theme preferences per-user in localStorage.
- Achieve WCAG 2.1 AA contrast ratios for primary color on white/dark backgrounds.
- Maintain all existing functionality and navigation patterns.

**Non-Goals:**
- No backend API changes or new endpoints.
- No redesign of overall layout structure (sidebar + content area remains).
- No migration away from shadcn/ui or Tailwind CSS.
- No new feature development (no new pages or capabilities).
- No mobile-first responsive redesign (tablet + desktop only, as current).
- No changes to i18n architecture.
- No refactoring of API layer or data fetching patterns.

## Decisions

### Decision 1: Color system — oklch conversion for `#AE1C3F`

**Choice:** Convert `#AE1C3F` to oklch and set as `--primary` in `:root` and derive a lighter/darker variant for `.dark`.

**Rationale:** The existing design system uses oklch throughout. Converting hex to oklch maintains consistency and allows Tailwind's opacity modifier syntax (`bg-primary/90`) to work correctly.

**Color values:**
- Light theme `--primary`: `oklch(0.44 0.18 15)` (≈ `#AE1C3F`)
- Light theme `--primary-foreground`: `oklch(0.98 0.01 15)` (white with warm tint)
- Dark theme `--primary`: `oklch(0.55 0.20 15)` (lighter for dark bg readability)
- Dark theme `--primary-foreground`: `oklch(0.98 0 0)` (pure white)
- `--ring` and `--sidebar-primary`, `--sidebar-ring` follow `--primary` in each mode.

**Contrast verification needed:**
- `#AE1C3F` on white → ratio ~5.5:1 ✓ (AA for normal text)
- White on `#AE1C3F` → ratio ~5.5:1 ✓ (AA for button text)
- Dark variant on dark bg → must verify ≥4.5:1

**Alternatives considered:**
- HSL values: Rejected because existing system uses oklch exclusively.
- CSS `color-mix()`: Rejected for broader compatibility.

### Decision 2: Destructive color differentiation

**Choice:** Shift `--destructive` to a distinct orange-red (`oklch(0.60 0.22 35)` in light, `oklch(0.70 0.19 35)` in dark) — perceptually orange compared to the deep crimson primary.

**Rationale:** With primary now being deep red, destructive must be visually distinct. Orange-red is universally recognized as "warning/danger" and is far enough on the hue wheel (hue 35 vs 15) to be distinguishable.

**Additional measures:**
- All destructive buttons must include text labels ("Delete", "Remove") not just icons.
- All destructive operations must use `ConfirmDialog`.
- Destructive buttons use `variant="destructive"` which applies the `--destructive` token automatically.

**Alternatives considered:**
- Bright red (#FF0000): Too harsh, poor accessibility.
- Yellow/amber: Not semantically "danger" enough in this context.

### Decision 3: RBAC UI pattern — `useIsAdmin()` hook

**Choice:** Create a thin `useIsAdmin()` hook wrapping `useAuthStore` for clean component-level role checks.

```typescript
export function useIsAdmin() {
  const user = useAuthStore((s) => s.user)
  return user?.role === 'admin'
}
```

**Rationale:** Avoids repeating `useAuthStore().user?.role === 'admin'` in every component. Already partially done in `AppSidebar.tsx` but not extracted.

**UI patterns by component type:**
- **Navigation items**: Conditionally rendered (not rendered at all for unauthorized roles).
- **Action buttons** (delete, edit, reprocess): Conditionally rendered — hidden entirely for non-admins (not disabled, to avoid clutter).
- **Checkboxes** (source → notebook assignment): Rendered as disabled with tooltip "Only admins can assign sources to notebooks".
- **Create dialogs**: Hidden from dropdown for non-admins (no source/notebook/podcast creation).
- **Pages** (settings, admin): Protected by `AdminRoute` showing Access Denied.

**Alternatives considered:**
- Disabled buttons with tooltips everywhere: Rejected — too much visual noise for features users never have access to.
- Permission-based system (fine-grained): Over-engineering for binary admin/user model.

### Decision 4: Change Password — modal dialog approach

**Choice:** Replace `/settings/change-password` page with a `ChangePasswordDialog` component triggered from sidebar.

**Rationale:** User requirement explicitly states "show as dialog instead of page beside sidebar." Modal dialogs are standard for quick single-form actions. Removes a route, simplifies navigation.

**Implementation:**
- New component `ChangePasswordDialog.tsx` in `components/auth/`.
- Triggered by clicking "Change Password" in sidebar (instead of navigating to a route).
- Form fields: current password, new password, confirm new password.
- Validation: Zod schema, react-hook-form.
- On success: toast notification, close dialog.
- On error: inline error message.

**Alternatives considered:**
- Keep as page but in a panel/card: Rejected — user explicitly wants dialog.
- Drawer/sheet: Viable but dialog is more standard for forms.

### Decision 5: Theme localStorage namespacing

**Choice:** Change theme store's `name` from `'theme-storage'` to `'theme-storage-${userId}'` pattern. On logout, clear all user-specific localStorage keys.

**Implementation:**
- `theme-store.ts`: Accept userId parameter, construct dynamic storage key.
- `auth-store.ts` logout: Clear `theme-storage-*` keys from localStorage.
- After login: `fetchPreferences()` already syncs server → local. Add explicit `theme-store` re-initialization with user ID.

**Alternatives considered:**
- Single key with JSON object per user: More complex parsing, no benefit.
- Server-only theme (no localStorage): Would cause flash of unstyled content on page load.

### Decision 6: Hard-coded color audit — semantic token replacement

**Choice:** Replace all `text-blue-*`, `bg-blue-*`, `border-blue-*` classes with semantic equivalents.

**Mapping:**
| Current | Replacement |
|---------|-------------|
| `text-blue-600` | `text-primary` |
| `bg-blue-50` | `bg-primary/10` |
| `bg-blue-100` | `bg-primary/15` |
| `border-blue-200` | `border-primary/20` |
| `bg-blue-600` (progress) | `bg-primary` |
| `text-blue-500` (spinner) | `text-primary` |
| `bg-blue-950` (dark info) | `bg-primary/15` |
| `text-blue-700` (info text) | `text-primary` |
| `text-blue-300` (dark info) | `text-primary` |
| `prose-a:text-blue-600` | `prose-a:text-primary` |

**Files affected:** `SourceCard.tsx`, `SourceDetailContent.tsx`, `ChatPanel.tsx`, `SourceTypeStep.tsx`, `api-keys/page.tsx`, `RebuildEmbeddings.tsx`.

## Risks / Trade-offs

- **[Risk] Primary ≈ Destructive confusion** → Mitigated by shifting destructive hue to 35° (orange-red) vs primary at 15° (crimson), plus mandatory text labels and confirm dialogs on all destructive actions.
- **[Risk] oklch conversion inaccuracy** → Mitigated by visual verification in browser. Will test with dev tools color picker.
- **[Risk] Theme flash on login** → Mitigated by keeping localStorage for instant theme application + server sync on login. Script in `<head>` applies theme before React hydration.
- **[Risk] Breaking existing admin workflows** → Mitigated by only hiding UI for non-admins; admin experience remains identical.
- **[Risk] Source list missing delete for admins** → Not a risk; delete button is conditionally rendered only for admins, same pattern used successfully in sidebar.
- **[Risk] Change Password dialog accessibility** → Mitigated by using Radix Dialog which handles focus trapping, keyboard navigation, and aria attributes automatically.
- **[Trade-off] Hiding vs disabling unauthorized actions** → Chose hiding for most actions (cleaner UI) and disabling only for checkboxes (where context is useful). This may confuse admins who expect to see what non-admins see.
