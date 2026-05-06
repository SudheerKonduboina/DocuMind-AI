import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './modules/auth/store/authStore'
import LoginPage from './modules/auth/pages/LoginPage'
import RegisterPage from './modules/auth/pages/RegisterPage'
import DashboardPage from './modules/auth/pages/DashboardPage'
import UploadPage from './modules/upload/pages/UploadPage'
import ChatPage from './modules/chat/pages/ChatPage'
import MediaLibraryPage from './modules/media/pages/MediaLibraryPage'
import SummaryPage from './modules/summary/pages/SummaryPage'
import PlayerPage from './modules/player/pages/PlayerPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/upload" element={
          <ProtectedRoute>
            <UploadPage />
          </ProtectedRoute>
        } />
        <Route path="/chat/:chatId?" element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        } />
        <Route path="/library" element={
          <ProtectedRoute>
            <MediaLibraryPage />
          </ProtectedRoute>
        } />
        <Route path="/summary/:documentId" element={
          <ProtectedRoute>
            <SummaryPage />
          </ProtectedRoute>
        } />
        <Route path="/player/:documentId" element={
          <ProtectedRoute>
            <PlayerPage />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}

export default App
