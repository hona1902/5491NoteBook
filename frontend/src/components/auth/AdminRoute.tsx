'use client'

import { useAuthStore } from '@/lib/stores/auth-store'
import { AccessDenied } from '@/components/common/AccessDenied'

interface AdminRouteProps {
  children: React.ReactNode
}

export function AdminRoute({ children }: AdminRouteProps) {
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'

  if (!isAdmin) {
    return <AccessDenied />
  }

  return <>{children}</>
}
