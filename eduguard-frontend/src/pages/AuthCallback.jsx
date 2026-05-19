import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

const AuthCallback = () => {
  const navigate = useNavigate()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const accessToken = params.get('access_token')
    const refreshToken = params.get('refresh_token')
    const email = params.get('email')

    if (accessToken) {
      localStorage.setItem('eduguard_access_token', accessToken)
      if (refreshToken) localStorage.setItem('eduguard_refresh_token', refreshToken)
      if (email) localStorage.setItem('eduguard_user_email', email)
      toast.success('Signed in successfully')
      navigate('/tutor', { replace: true })
      return
    }

    toast.error('Google sign-in did not return a session')
    navigate('/login', { replace: true })
  }, [navigate])

  return (
    <div style={{ minHeight: '100vh', background: '#0A0F1E', padding: '120px 24px 60px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <p style={{ fontFamily: 'Syne', color: '#00D4FF', fontWeight: 700 }}>Completing sign-in...</p>
    </div>
  )
}

export default AuthCallback
