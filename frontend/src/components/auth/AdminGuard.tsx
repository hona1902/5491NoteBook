'use client'

import { useAuthStore } from '@/lib/stores/auth-store'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { AccessDenied } from '@/components/common/AccessDenied'

export function AdminGuard({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, hasHydrated } = useAuthStore()

  // Show spinner while auth store is hydrating
  if (!hasHydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  // Show Access Denied instead of silently redirecting
  if (isAuthenticated && user && user.role !== 'admin') {
    return <AccessDenied />
  }

  // Still loading user data
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return <>{children}</>
}
