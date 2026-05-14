'use client'

import { useAuthStore } from '@/lib/stores/auth-store'
import { useTranslation } from '@/lib/hooks/use-translation'
import { ShieldAlert } from 'lucide-react'

interface AdminRouteProps {
  children: React.ReactNode
}

export function AdminRoute({ children }: AdminRouteProps) {
  const { t } = useTranslation()
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center px-6">
        <div className="rounded-full bg-destructive/10 p-4">
          <ShieldAlert className="h-10 w-10 text-destructive" />
        </div>
        <h1 className="text-2xl font-bold text-foreground">
          {t('common.accessDenied', 'Access Denied')}
        </h1>
        <p className="text-muted-foreground max-w-md">
          {t(
            'common.adminRequired',
            'You do not have permission to access this page. Please contact an administrator if you need access.'
          )}
        </p>
      </div>
    )
  }

  return <>{children}</>
}
