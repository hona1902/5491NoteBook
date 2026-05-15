import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Theme = 'light' | 'dark' | 'system'

const THEME_KEY_PREFIX = 'theme-storage'
const GLOBAL_THEME_KEY = 'theme-storage'

/**
 * Get the localStorage key for a specific user's theme.
 * Falls back to the global key when no userId is provided.
 */
function getThemeKey(userId?: string | null): string {
  return userId ? `${THEME_KEY_PREFIX}-${userId}` : GLOBAL_THEME_KEY
}

interface ThemeState {
  theme: Theme
  currentUserId: string | null
  setTheme: (theme: Theme) => void
  getSystemTheme: () => 'light' | 'dark'
  getEffectiveTheme: () => 'light' | 'dark'
  /** Bind the theme store to a specific user — loads their saved theme or falls back to system default */
  bindToUser: (userId: string) => void
  /** Unbind from the current user — resets to system default and removes in-memory user association */
  unbindUser: () => void
}

function applyThemeToDocument(theme: Theme, getSystemTheme: () => 'light' | 'dark') {
  if (typeof window === 'undefined') return
  const root = window.document.documentElement
  const effectiveTheme = theme === 'system' ? getSystemTheme() : theme
  root.classList.remove('light', 'dark')
  root.classList.add(effectiveTheme)
  root.setAttribute('data-theme', effectiveTheme)
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      currentUserId: null,

      setTheme: (theme: Theme) => {
        const { currentUserId, getSystemTheme } = get()
        set({ theme })

        // Save to user-specific key if bound
        if (typeof window !== 'undefined' && currentUserId) {
          const key = getThemeKey(currentUserId)
          try {
            localStorage.setItem(key, JSON.stringify({ state: { theme }, version: 0 }))
          } catch {
            // localStorage not available
          }
        }

        applyThemeToDocument(theme, getSystemTheme)
      },

      getSystemTheme: () => {
        if (typeof window !== 'undefined') {
          return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        }
        return 'light'
      },

      getEffectiveTheme: () => {
        const { theme } = get()
        return theme === 'system' ? get().getSystemTheme() : theme
      },

      bindToUser: (userId: string) => {
        const { getSystemTheme } = get()
        const key = getThemeKey(userId)

        let userTheme: Theme = 'system'
        if (typeof window !== 'undefined') {
          try {
            const stored = localStorage.getItem(key)
            if (stored) {
              const parsed = JSON.parse(stored)
              if (parsed?.state?.theme) {
                userTheme = parsed.state.theme as Theme
              }
            }
          } catch {
            // Corrupted or missing data, use system default
          }
        }

        set({ theme: userTheme, currentUserId: userId })
        applyThemeToDocument(userTheme, getSystemTheme)
      },

      unbindUser: () => {
        const { getSystemTheme } = get()
        set({ theme: 'system', currentUserId: null })
        applyThemeToDocument('system', getSystemTheme)
      },
    }),
    {
      name: GLOBAL_THEME_KEY,
      partialize: (state) => ({ theme: state.theme }),
    }
  )
)

// Hook for components to use theme
export function useTheme() {
  const { theme, setTheme, getEffectiveTheme } = useThemeStore()

  return {
    theme,
    setTheme,
    effectiveTheme: getEffectiveTheme(),
    isDark: getEffectiveTheme() === 'dark',
  }
}