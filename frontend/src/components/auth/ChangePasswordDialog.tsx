'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Loader2, Eye, EyeOff } from 'lucide-react'
import { toast } from 'sonner'
import { authApi } from '@/lib/api/auth'
import { useTranslation } from '@/lib/hooks/use-translation'
import { isAxiosError } from 'axios'

interface ChangePasswordFormValues {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

interface ChangePasswordDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ChangePasswordDialog({ open, onOpenChange }: ChangePasswordDialogProps) {
  const { t } = useTranslation()
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ChangePasswordFormValues>({
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  })

  const newPassword = watch('newPassword')

  const onSubmit = async (data: ChangePasswordFormValues) => {
    setServerError(null)

    try {
      await authApi.changePassword(data.currentPassword, data.newPassword)
      toast.success(t('settings.passwordChanged', 'Password changed successfully'))
      reset()
      onOpenChange(false)
    } catch (err) {
      if (isAxiosError(err)) {
        const status = err.response?.status
        const detail = err.response?.data?.detail

        if (status === 400 || status === 401) {
          setServerError(detail || t('settings.wrongCurrentPassword', 'Current password is incorrect'))
        } else {
          setServerError(detail || t('common.error', 'An error occurred. Please try again.'))
        }
      } else {
        setServerError(t('common.error', 'An error occurred. Please try again.'))
      }
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      reset()
      setServerError(null)
      setShowCurrentPassword(false)
      setShowNewPassword(false)
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t('navigation.changePassword', 'Change Password')}</DialogTitle>
          <DialogDescription>
            {t('settings.changePasswordDesc', 'Enter your current password and choose a new one.')}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Server error */}
          {serverError && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive" role="alert">
              {serverError}
            </div>
          )}

          {/* Current Password */}
          <div className="space-y-2">
            <Label htmlFor="cp-current">{t('settings.currentPassword', 'Current Password')}</Label>
            <div className="relative">
              <input
                id="cp-current"
                type={showCurrentPassword ? 'text' : 'password'}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm pr-10 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                autoComplete="current-password"
                disabled={isSubmitting}
                {...register('currentPassword', {
                  required: t('settings.fieldRequired', 'This field is required'),
                })}
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                tabIndex={-1}
                aria-label={showCurrentPassword ? 'Hide password' : 'Show password'}
              >
                {showCurrentPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.currentPassword && (
              <p className="text-xs text-destructive">{errors.currentPassword.message}</p>
            )}
          </div>

          {/* New Password */}
          <div className="space-y-2">
            <Label htmlFor="cp-new">{t('settings.newPassword', 'New Password')}</Label>
            <div className="relative">
              <input
                id="cp-new"
                type={showNewPassword ? 'text' : 'password'}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm pr-10 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                autoComplete="new-password"
                disabled={isSubmitting}
                {...register('newPassword', {
                  required: t('settings.fieldRequired', 'This field is required'),
                  minLength: {
                    value: 6,
                    message: t('settings.passwordMinLength', 'Password must be at least 6 characters'),
                  },
                })}
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                tabIndex={-1}
                aria-label={showNewPassword ? 'Hide password' : 'Show password'}
              >
                {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.newPassword && (
              <p className="text-xs text-destructive">{errors.newPassword.message}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div className="space-y-2">
            <Label htmlFor="cp-confirm">{t('settings.confirmPassword', 'Confirm New Password')}</Label>
            <input
              id="cp-confirm"
              type="password"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              autoComplete="new-password"
              disabled={isSubmitting}
              {...register('confirmPassword', {
                required: t('settings.fieldRequired', 'This field is required'),
                validate: (value) =>
                  value === newPassword || t('settings.passwordMismatch', 'Passwords do not match'),
              })}
            />
            {errors.confirmPassword && (
              <p className="text-xs text-destructive">{errors.confirmPassword.message}</p>
            )}
          </div>

          <DialogFooter className="pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => handleOpenChange(false)} disabled={isSubmitting}>
              {t('common.cancel', 'Cancel')}
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              {t('settings.changePasswordBtn', 'Change Password')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
