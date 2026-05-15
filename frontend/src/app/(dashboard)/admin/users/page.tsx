'use client'

import { useState, useEffect, useCallback } from 'react'
import { AdminGuard } from '@/components/auth/AdminGuard'
import { adminUsersApi, CreateUserRequest } from '@/lib/api/adminUsers'
import type { AppUser } from '@/lib/stores/auth-store'
import { useAuthStore } from '@/lib/stores/auth-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { toast } from 'sonner'
import { AppShell } from '@/components/layout/AppShell'
import { useTranslation } from '@/lib/hooks/use-translation'
import {
  Plus,
  Users,
  Shield,
  ShieldAlert,
  UserCheck,
  UserX,
  KeyRound,
  Trash2,
  RefreshCw,
  AlertCircle,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { getDateLocale } from '@/lib/utils/date-locale'

function UsersContent() {
  const { t, language } = useTranslation()
  const currentUser = useAuthStore((s) => s.user)
  const [users, setUsers] = useState<AppUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [resetPasswordOpen, setResetPasswordOpen] = useState<string | null>(null)
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '', role: 'user' })
  const [newPassword, setNewPassword] = useState('')
  const [creating, setCreating] = useState(false)
  const [resettingPassword, setResettingPassword] = useState(false)

  // Confirm dialogs
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; user: AppUser | null }>({ open: false, user: null })
  const [deactivateDialog, setDeactivateDialog] = useState<{ open: boolean; user: AppUser | null }>({ open: false, user: null })
  const [deleting, setDeleting] = useState(false)
  const [toggling, setToggling] = useState(false)

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await adminUsersApi.list()
      setUsers(data)
    } catch {
      setError(t('admin.failedLoadUsers', 'Failed to load users'))
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    try {
      await adminUsersApi.create(newUser as CreateUserRequest)
      toast.success(t('admin.userCreated', 'User created'))
      setCreateOpen(false)
      setNewUser({ username: '', email: '', password: '', role: 'user' })
      fetchUsers()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      toast.error(error?.response?.data?.detail || t('admin.failedCreateUser', 'Failed to create user'))
    } finally {
      setCreating(false)
    }
  }

  const handleToggleActive = async () => {
    const user = deactivateDialog.user
    if (!user) return
    setToggling(true)
    try {
      await adminUsersApi.update(user.id, { is_active: !user.is_active })
      toast.success(
        user.is_active
          ? t('admin.userDeactivated', 'User deactivated')
          : t('admin.userActivated', 'User activated')
      )
      setDeactivateDialog({ open: false, user: null })
      fetchUsers()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      toast.error(error?.response?.data?.detail || t('admin.failedUpdateUser', 'Failed to update user'))
    } finally {
      setToggling(false)
    }
  }

  const handleDelete = async () => {
    const user = deleteDialog.user
    if (!user) return

    // Self-deletion protection
    if (user.id === currentUser?.id) {
      toast.error(t('admin.cannotDeleteSelf', 'You cannot delete your own account'))
      setDeleteDialog({ open: false, user: null })
      return
    }

    setDeleting(true)
    try {
      await adminUsersApi.delete(user.id)
      toast.success(t('admin.userDeleted', 'User deleted'))
      setDeleteDialog({ open: false, user: null })
      fetchUsers()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      toast.error(error?.response?.data?.detail || t('admin.failedDeleteUser', 'Failed to delete user'))
    } finally {
      setDeleting(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!resetPasswordOpen) return
    setResettingPassword(true)
    try {
      await adminUsersApi.resetPassword(resetPasswordOpen, newPassword)
      toast.success(t('admin.passwordReset', 'Password reset'))
      setResetPasswordOpen(null)
      setNewPassword('')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      toast.error(error?.response?.data?.detail || t('admin.failedResetPassword', 'Failed to reset password'))
    } finally {
      setResettingPassword(false)
    }
  }

  // Determine if user is self (for protection)
  const isSelf = (user: AppUser) => user.id === currentUser?.id

  // Loading state
  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <LoadingSpinner />
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 p-8">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <p className="text-destructive font-medium">{error}</p>
        <Button variant="outline" onClick={fetchUsers}>
          <RefreshCw className="h-4 w-4 mr-2" />
          {t('common.retry', 'Retry')}
        </Button>
      </div>
    )
  }

  // Empty state
  if (users.length === 0) {
    return (
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Users className="h-6 w-6" />
            {t('admin.userManagement', 'User Management')}
          </h1>
        </div>
        <EmptyState
          icon={Users}
          title={t('admin.noUsersFound', 'No users found')}
          description={t('admin.noUsersDesc', 'Create the first user to get started')}
        />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Users className="h-6 w-6" />
            {t('admin.userManagement', 'User Management')}
          </h1>
          <Badge variant="secondary" className="text-xs">
            {users.length} {users.length === 1 ? t('admin.user', 'user') : t('admin.users', 'users')}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchUsers}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                {t('admin.createUser', 'Create User')}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('admin.createNewUser', 'Create New User')}</DialogTitle>
                <DialogDescription>
                  {t('admin.createUserDesc', 'Add a new user to the system')}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="create-username">{t('common.username', 'Username')}</Label>
                  <Input
                    id="create-username"
                    name="username"
                    placeholder={t('admin.usernamePlaceholder', 'Enter username')}
                    value={newUser.username}
                    onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                    required
                    minLength={3}
                    autoComplete="off"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="create-email">{t('common.email', 'Email')}</Label>
                  <Input
                    id="create-email"
                    name="email"
                    type="email"
                    placeholder={t('admin.emailPlaceholder', 'Enter email')}
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    required
                    autoComplete="off"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="create-password">{t('common.password', 'Password')}</Label>
                  <Input
                    id="create-password"
                    name="password"
                    type="password"
                    placeholder={t('admin.passwordPlaceholder', 'Min 8 characters')}
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    required
                    minLength={8}
                    autoComplete="new-password"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="create-role">{t('common.role', 'Role')}</Label>
                  <Select
                    value={newUser.role}
                    onValueChange={(value) => setNewUser({ ...newUser, role: value })}
                  >
                    <SelectTrigger id="create-role">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user">{t('admin.roleUser', 'User')}</SelectItem>
                      <SelectItem value="admin">{t('admin.roleAdmin', 'Admin')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" className="w-full" disabled={creating}>
                  {creating ? t('common.creating', 'Creating...') : t('admin.createUser', 'Create User')}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Users Table */}
      <div className="rounded-md border overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">{t('common.username', 'Username')}</th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground hidden sm:table-cell">{t('common.email', 'Email')}</th>
              <th className="h-12 px-4 text-center align-middle font-medium text-muted-foreground">{t('common.role', 'Role')}</th>
              <th className="h-12 px-4 text-center align-middle font-medium text-muted-foreground">{t('common.status', 'Status')}</th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground hidden md:table-cell">{t('admin.lastLogin', 'Last Login')}</th>
              <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">{t('common.actions', 'Actions')}</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b hover:bg-muted/50 transition-colors">
                <td className="h-14 px-4">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{user.username}</span>
                    {isSelf(user) && (
                      <Badge variant="outline" className="text-xs text-primary border-primary/50">
                        {t('admin.you', 'You')}
                      </Badge>
                    )}
                  </div>
                </td>
                <td className="h-14 px-4 text-muted-foreground text-sm hidden sm:table-cell">
                  {user.email}
                </td>
                <td className="h-14 px-4 text-center">
                  <Badge variant={user.role === 'admin' ? 'default' : 'secondary'} className="gap-1">
                    {user.role === 'admin' ? <Shield className="h-3 w-3" /> : null}
                    {user.role === 'admin' ? t('admin.roleAdmin', 'Admin') : t('admin.roleUser', 'User')}
                  </Badge>
                </td>
                <td className="h-14 px-4 text-center">
                  {user.is_active ? (
                    <Badge variant="outline" className="text-green-600 border-green-200 gap-1">
                      <UserCheck className="h-3 w-3" />
                      {t('admin.active', 'Active')}
                    </Badge>
                  ) : (
                    <Badge variant="destructive" className="gap-1">
                      <UserX className="h-3 w-3" />
                      {t('admin.inactive', 'Inactive')}
                    </Badge>
                  )}
                </td>
                <td className="h-14 px-4 text-sm text-muted-foreground hidden md:table-cell">
                  {user.last_login_at
                    ? formatDistanceToNow(new Date(user.last_login_at), {
                        addSuffix: true,
                        locale: getDateLocale(language),
                      })
                    : t('admin.never', 'Never')}
                </td>
                <td className="h-14 px-4 text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      title={user.is_active ? t('admin.deactivate', 'Deactivate') : t('admin.activate', 'Activate')}
                      onClick={() => setDeactivateDialog({ open: true, user })}
                      disabled={isSelf(user)}
                    >
                      {user.is_active ? (
                        <UserX className="h-4 w-4" />
                      ) : (
                        <UserCheck className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      title={t('admin.resetPassword', 'Reset Password')}
                      onClick={() => setResetPasswordOpen(user.id)}
                    >
                      <KeyRound className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      title={t('common.delete', 'Delete')}
                      onClick={() => setDeleteDialog({ open: true, user })}
                      disabled={isSelf(user)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Reset Password Dialog */}
      <Dialog open={!!resetPasswordOpen} onOpenChange={() => setResetPasswordOpen(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('admin.resetPassword', 'Reset Password')}</DialogTitle>
            <DialogDescription>
              {t('admin.resetPasswordDesc', 'Set a new password for this user')}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="reset-password">{t('admin.newPassword', 'New Password')}</Label>
              <Input
                id="reset-password"
                name="new-password"
                type="password"
                placeholder={t('admin.passwordPlaceholder', 'Min 8 characters')}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>
            <Button type="submit" className="w-full" disabled={resettingPassword}>
              {resettingPassword ? t('common.saving', 'Saving...') : t('admin.resetPassword', 'Reset Password')}
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirm Dialog */}
      <ConfirmDialog
        open={deleteDialog.open}
        onOpenChange={(open) => setDeleteDialog({ open, user: deleteDialog.user })}
        title={t('admin.deleteUser', 'Delete User')}
        description={
          t('admin.deleteUserConfirm', 'Are you sure you want to delete "{username}"? This action cannot be undone.')
            .replace('{username}', deleteDialog.user?.username || '')
        }
        confirmText={t('common.delete', 'Delete')}
        confirmVariant="destructive"
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {/* Deactivate/Activate Confirm Dialog */}
      <ConfirmDialog
        open={deactivateDialog.open}
        onOpenChange={(open) => setDeactivateDialog({ open, user: deactivateDialog.user })}
        title={
          deactivateDialog.user?.is_active
            ? t('admin.deactivateUser', 'Deactivate User')
            : t('admin.activateUser', 'Activate User')
        }
        description={
          deactivateDialog.user?.is_active
            ? t('admin.deactivateConfirm', 'Deactivate "{username}"? They will not be able to log in until reactivated.')
                .replace('{username}', deactivateDialog.user?.username || '')
            : t('admin.activateConfirm', 'Activate "{username}"? They will be able to log in again.')
                .replace('{username}', deactivateDialog.user?.username || '')
        }
        confirmText={
          deactivateDialog.user?.is_active
            ? t('admin.deactivate', 'Deactivate')
            : t('admin.activate', 'Activate')
        }
        confirmVariant={deactivateDialog.user?.is_active ? 'destructive' : 'default'}
        onConfirm={handleToggleActive}
        isLoading={toggling}
      />
    </div>
  )
}

export default function AdminUsersPage() {
  return (
    <AdminGuard>
      <AppShell>
        <UsersContent />
      </AppShell>
    </AdminGuard>
  )
}
