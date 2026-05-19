import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/ui/Navbar'
import Landing from './pages/Landing'
import TutorPage from './pages/TutorPage'
import ExamPage from './pages/ExamPage'
import Dashboard from './pages/Dashboard'
import AuthPage from './pages/AuthPage'
import AuthCallback from './pages/AuthCallback'

const isSignedIn = () => Boolean(localStorage.getItem('eduguard_access_token'))

const ProtectedRoute = ({ children }) => {
  const location = useLocation()

  if (!isSignedIn()) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return children
}

const PublicAuthRoute = ({ children }) => {
  if (isSignedIn()) {
    return <Navigate to="/tutor" replace />
  }

  return children
}

const App = () => {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#0D1530',
            color: '#F0F4FF',
            border: '1px solid rgba(0,212,255,0.2)',
            fontFamily: 'DM Sans',
            fontSize: 14,
          },
          success: { iconTheme: { primary: '#00FF88', secondary: '#0D1530' } },
          error: { iconTheme: { primary: '#FF3366', secondary: '#0D1530' } },
        }}
      />
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to={isSignedIn() ? '/tutor' : '/login'} replace />} />
        <Route path="/home" element={<ProtectedRoute><Landing /></ProtectedRoute>} />
        <Route path="/tutor" element={<ProtectedRoute><TutorPage /></ProtectedRoute>} />
        <Route path="/exam" element={<ProtectedRoute><ExamPage /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/login" element={<PublicAuthRoute><AuthPage mode="login" /></PublicAuthRoute>} />
        <Route path="/signup" element={<PublicAuthRoute><AuthPage mode="signup" /></PublicAuthRoute>} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
