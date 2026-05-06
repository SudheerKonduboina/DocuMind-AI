import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../modules/auth/store/authStore'
import { LayoutDashboard, FileText, MessageSquare, LogOut, Sparkles } from 'lucide-react'
import ThemeToggle from './ThemeToggle'

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-luxury-cream dark:bg-luxury-dark transition-colors duration-500">
      {/* Glass Navigation */}
      <nav className="fixed top-6 left-0 right-0 z-50 px-6">
        <div className="max-w-6xl mx-auto glass-nav flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="p-2 bg-luxury-sage rounded-xl group-hover:rotate-12 transition-transform duration-500">
              <Sparkles size={24} className="text-white" />
            </div>
            <span className="text-xl font-serif font-bold tracking-tight luxury-gradient-text hidden sm:block">
              DocuMind AI
            </span>
          </Link>

          <div className="flex items-center gap-1 sm:gap-4">
            <Link
              to="/"
              className={`p-3 rounded-full transition-all duration-300 ${
                isActive('/') ? 'bg-luxury-sage text-white shadow-lg shadow-luxury-sage/20' : 'hover:bg-luxury-sage/10 text-luxury-dark dark:text-white'
              }`}
            >
              <LayoutDashboard size={20} />
            </Link>
            <Link
              to="/library"
              className={`p-3 rounded-full transition-all duration-300 ${
                isActive('/library') ? 'bg-luxury-sage text-white shadow-lg shadow-luxury-sage/20' : 'hover:bg-luxury-sage/10 text-luxury-dark dark:text-white'
              }`}
            >
              <FileText size={20} />
            </Link>
            <Link
              to="/chat"
              className={`p-3 rounded-full transition-all duration-300 ${
                isActive('/chat') || location.pathname.startsWith('/chat/') ? 'bg-luxury-sage text-white shadow-lg shadow-luxury-sage/20' : 'hover:bg-luxury-sage/10 text-luxury-dark dark:text-white'
              }`}
            >
              <MessageSquare size={20} />
            </Link>
            
            <div className="w-px h-6 bg-luxury-dark/10 dark:bg-white/10 mx-2" />
            
            <ThemeToggle />
            
            <button
              onClick={handleLogout}
              className="p-3 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 transition-all duration-300"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className={`mx-auto transition-all duration-500 ${
        location.pathname.startsWith('/chat') 
          ? 'max-w-full pt-20 p-0' 
          : 'max-w-7xl pt-32 p-6 sm:p-8'
      }`}>
        <div className="animate-fade-in h-full">
          <Outlet />
        </div>
      </main>

      {/* Luxury Footer */}
      <footer className="max-w-7xl mx-auto p-12 mt-12 border-t border-luxury-dark/5 dark:border-white/5">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-8 opacity-40 grayscale hover:grayscale-0 transition-all duration-500">
          <p className="font-serif text-2xl tracking-tighter">DIGITAL HEROES</p>
          <div className="flex gap-8 text-xs uppercase tracking-widest font-medium">
            <span className="cursor-pointer hover:text-luxury-sage transition-colors">Privacy</span>
            <span className="cursor-pointer hover:text-luxury-sage transition-colors">Terms</span>
            <span className="cursor-pointer hover:text-luxury-sage transition-colors">Contact</span>
          </div>
          <p className="text-xs">© 2026 — ALL RIGHTS RESERVED</p>
        </div>
      </footer>
    </div>
  )
}
