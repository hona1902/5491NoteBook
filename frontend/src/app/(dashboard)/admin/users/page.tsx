'use client'

import { useState, useEffect } from 'react'
import { AdminGuard } from '@/components/auth/AdminGuard'
import { adminUsersApi, CreateUserRequest } from '@/lib/api/adminUsers'
import type { AppUser } from '@/lib/stores/auth-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { AppShell } from '@/components/layout/AppShell'

function UsersContent() {
  const [users, setUsers] = useState<AppUser[]>([])
  const [loading, setLoading] = useState(true)
  const [createOpen, setCreateOpen] = useState(false)
  const [resetPasswordOpen, setResetPasswordOpen] = useState<string | null>(null)
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '', role: 'user' })
  const [newPassword, setNewPassword] = useState('')

  const fetchUsers = async () => {
    try {
      const data = await adminUsersApi.list()
      setUsers(data)
    } catch (err) {
      toast.error('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await adminUsersApi.create(newUser as CreateUserRequest)
      toast.success('User created')
      setCreateOpen(false)
      setNewUser({ username: '', email: '', password: '', role: 'user' })
      fetchUsers()
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to create user')
    }
  }

  const handleToggleActive = async (user: AppUser) => {
    try {
      await adminUsersApi.update(user.id, { is_active: !user.is_active })
      toast.success(`User ${user.is_active ? 'deactivated' : 'activated'}`)
      fetchUsers()
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to update user')
    }
  }

  const handleDelete = async (user: AppUser) => {
    if (!confirm(`Delete user "${user.username}"? This cannot be undone.`)) return
    try {
      await adminUsersApi.delete(user.id)
      toast.success('User deleted')
      fetchUsers()
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to delete user')
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!resetPasswordOpen) return
    try {
      await adminUsersApi.resetPassword(resetPasswordOpen, newPassword)
      toast.success('Password reset')
      setResetPasswordOpen(null)
      setNewPassword('')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to reset password')
    }
  }

  if (loading) {
    return <div className="p-8 text-center text-muted-foreground">Loading users...</div>
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">User Management</h1>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>Create User</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New User</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <Input
                placeholder="Username"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                required
                minLength={3}
              />
              <Input
                type="email"
                placeholder="Email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                required
              />
              <Input
                type="password"
                placeholder="Password (min 8 characters)"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                required
                minLength={8}
              />
              <select
                className="w-full border rounded px-3 py-2 bg-background"
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
              <Button type="submit" className="w-full">Create</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-3">
        {users.map((user) => (
          <Card key={user.id}>
            <CardContent className="flex items-center justify-between py-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{user.username}</span>
                  <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                    {user.role}
                  </Badge>
                  {!user.is_active && (
                    <Badge variant="destructive">Inactive</Badge>
                  )}
                </div>
                <div className="text-sm text-muted-foreground">{user.email}</div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleToggleActive(user)}
                >
                  {user.is_active ? 'Deactivate' : 'Activate'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setResetPasswordOpen(user.id)}
                >
                  Reset Password
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDelete(user)}
                >
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={!!resetPasswordOpen} onOpenChange={() => setResetPasswordOpen(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reset Password</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleResetPassword} className="space-y-4">
            <Input
              type="password"
              placeholder="New password (min 8 characters)"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={8}
            />
            <Button type="submit" className="w-full">Reset Password</Button>
          </form>
        </DialogContent>
      </Dialog>
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
