import { useAuthStore } from '@/lib/stores/auth-store'

/**
 * Hook to check if the current user has admin role.
 * Reads from the auth store's user object.
 *
 * @returns `true` if the authenticated user's role is 'admin', `false` otherwise.
 */
export function useIsAdmin(): boolean {
  const user = useAuthStore((state) => state.user)
  return user?.role === 'admin'
}
