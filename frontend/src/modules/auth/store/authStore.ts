import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authService, LoginData, RegisterData } from '../services/authService'

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  access_token: string | null
  isAuthenticated: boolean
  setUser: (user: User) => void
  setToken: (token: string) => void
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      access_token: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: true }),
      setToken: (token) => set({ access_token: token }),
      login: async (email, password) => {
        const response = await authService.login({ email, password })
        localStorage.setItem('access_token', response.access_token)
        set({
          user: response.user,
          access_token: response.access_token,
          isAuthenticated: true,
        })
      },
      register: async (email, password, fullName) => {
        const response = await authService.register({ email, password, full_name: fullName })
        // We don't automatically log in after registration in this flow, 
        // but we could. For now, let's just fulfill the promise.
      },
      logout: () => {
        localStorage.removeItem('access_token')
        set({ user: null, access_token: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
