'use client'

import { ShieldAlert } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { useTranslation } from '@/lib/hooks/use-translation'

interface AccessDeniedProps {
  /** Optional custom heading text */
  heading?: string
  /** Optional custom description text */
  description?: string
}

/**
 * Renders an Access Denied page for non-admin users who navigate to admin-only routes.
 * Displays a shield icon, heading, explanation, and a button to return to Notebooks.
 */
export function AccessDenied({ heading, description }: AccessDeniedProps) {
  const router = useRouter()
  const { t } = useTranslation()

  return (
    <div className="flex h-full min-h-[60vh] flex-col items-center justify-center gap-6 p-8 text-center" role="alert">
      <div className="rounded-full bg-destructive/10 p-4">
        <ShieldAlert className="h-12 w-12 text-destructive" aria-hidden="true" />
      </div>

      <div className="space-y-2 max-w-md">
        <h1 className="text-2xl font-bold tracking-tight">
          {heading || t('common.accessDenied', 'Access Denied')}
        </h1>
        <p className="text-muted-foreground">
          {description || t('common.accessDeniedDesc', 'You do not have permission to access this page. Contact your administrator if you believe this is an error.')}
        </p>
      </div>

      <Button
        onClick={() => router.push('/notebooks')}
        variant="outline"
        size="lg"
      >
        {t('common.goToNotebooks', 'Go to Notebooks')}
      </Button>
    </div>
  )
}
