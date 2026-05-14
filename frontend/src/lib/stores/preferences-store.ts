import { create } from 'zustand'
import { getApiUrl } from '@/lib/config'
import { useAuthStore } from '@/lib/stores/auth-store'
import { useThemeStore, type Theme } from '@/lib/stores/theme-store'

interface PreferencesState {
  isSyncing: boolean
  lastSyncError: string | null
  fetchPreferences: () => Promise<void>
  updateThemePreference: (theme: Theme) => Promise<void>
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const token = useAuthStore.getState().token
  if (!token) return {}
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

export const usePreferencesStore = create<PreferencesState>()((set) => ({
  isSyncing: false,
  lastSyncError: null,

  fetchPreferences: async () => {
    const token = useAuthStore.getState().token
    if (!token || token === 'not-required') return

    set({ isSyncing: true, lastSyncError: null })
    try {
      const apiUrl = await getApiUrl()
      const headers = await getAuthHeaders()
      const response = await fetch(`${apiUrl}/api/users/me/preferences`, {
        headers,
      })
      if (response.ok) {
        const data = await response.json()
        // Sync server theme → local store (server is source of truth)
        const serverTheme = data.theme as Theme
        useThemeStore.getState().setTheme(serverTheme)
      }
      // 404 or other non-ok is fine — user just has no prefs yet
    } catch (error) {
      console.error('Failed to fetch preferences:', error)
      set({ lastSyncError: 'Failed to fetch preferences' })
    } finally {
      set({ isSyncing: false })
    }
  },

  updateThemePreference: async (theme: Theme) => {
    // Apply locally immediately for instant feedback
    useThemeStore.getState().setTheme(theme)

    const token = useAuthStore.getState().token
    if (!token || token === 'not-required') return

    set({ isSyncing: true, lastSyncError: null })
    try {
      const apiUrl = await getApiUrl()
      const headers = await getAuthHeaders()
      await fetch(`${apiUrl}/api/users/me/preferences`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify({ theme }),
      })
    } catch (error) {
      console.error('Failed to sync theme preference:', error)
      set({ lastSyncError: 'Failed to sync theme' })
    } finally {
      set({ isSyncing: false })
    }
  },
}))
