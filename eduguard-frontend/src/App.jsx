import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/ui/Navbar'
import Landing from './pages/Landing'
import TutorPage from './pages/TutorPage'
import ExamPage from './pages/ExamPage'
import Dashboard from './pages/Dashboard'

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
        <Route path="/" element={<Landing />} />
        <Route path="/tutor" element={<TutorPage />} />
        <Route path="/exam" element={<ExamPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App