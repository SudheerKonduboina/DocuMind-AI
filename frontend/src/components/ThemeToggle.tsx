import { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark')
      setIsDark(true)
    } else {
      document.documentElement.classList.remove('dark')
      setIsDark(false)
    }
  }, [])

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark')
      localStorage.theme = 'light'
      setIsDark(false)
    } else {
      document.documentElement.classList.add('dark')
      localStorage.theme = 'dark'
      setIsDark(true)
    }
  }

  return (
    <button
      onClick={toggleTheme}
      className="p-3 rounded-full bg-white/50 dark:bg-white/10 hover:scale-110 active:scale-95 transition-all duration-300 backdrop-blur-md"
      aria-label="Toggle Theme"
    >
      {isDark ? (
        <Sun size={20} className="text-luxury-gold" />
      ) : (
        <Moon size={20} className="text-luxury-sage" />
      )}
    </button>
  )
}
