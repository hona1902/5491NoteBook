'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

/**
 * Legacy change-password route.
 * Password changes are now handled via the ChangePasswordDialog
 * accessible from the sidebar. This page redirects for backward compatibility.
 */
export default function ChangePasswordPage() {
  const router = useRouter()

  useEffect(() => {
    router.replace('/notebooks')
  }, [router])

  return null
}
