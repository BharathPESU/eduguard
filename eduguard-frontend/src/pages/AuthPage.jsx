import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { KeyRound, Lock, Mail, Shield } from 'lucide-react'
import toast from 'react-hot-toast'
import GlassCard from '../components/ui/GlassCard'
import { getGoogleAuthUrl, login, signup } from '../api/client'

const AuthPage = ({ mode }) => {
  const navigate = useNavigate()
  const isSignup = mode === 'signup'
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    if (!form.email.trim() || !form.password) return toast.error('Enter email and password')

    setLoading(true)
    try {
      const data = isSignup ? await signup(form) : await login(form)
      if (data.access_token) {
        localStorage.setItem('eduguard_access_token', data.access_token)
        if (data.session?.refresh_token) localStorage.setItem('eduguard_refresh_token', data.session.refresh_token)
        if (data.user?.email) localStorage.setItem('eduguard_user_email', data.user.email)
        toast.success('Signed in successfully')
        navigate('/tutor')
      } else {
        toast.success(data.message || 'Check your email to continue')
        navigate('/login')
      }
    } catch (e) {
      toast.error((isSignup ? 'Signup' : 'Login') + ' error: ' + (e.response?.data?.detail || e.message))
    }
    setLoading(false)
  }

  const startGoogle = () => {
    window.location.href = getGoogleAuthUrl()
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0A0F1E', padding: '110px 24px 60px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: '100%', maxWidth: 440 }}>
        <GlassCard accent="blue" hover={false}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28 }}>
            <div style={{ width: 42, height: 42, borderRadius: 12, background: 'rgba(0,212,255,0.12)', border: '1px solid rgba(0,212,255,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Shield size={18} color="#00D4FF" />
            </div>
            <div>
              <h1 style={{ fontFamily: 'Syne', fontSize: 24, fontWeight: 800, color: '#F0F4FF' }}>
                {isSignup ? 'Create Account' : 'Welcome Back'}
              </h1>
              <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', marginTop: 4 }}>
                {isSignup ? 'Sign up with Supabase email confirmation' : 'Log in to continue to EduGuard'}
              </p>
            </div>
          </div>

          <form onSubmit={submit}>
            <label style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0', display: 'block', marginBottom: 6 }}>Email</label>
            <div style={{ position: 'relative', marginBottom: 16 }}>
              <Mail size={16} color="#7B8DB0" style={{ position: 'absolute', left: 13, top: 13 }} />
              <input className="edu-input" type="email" value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                style={{ width: '100%', padding: '12px 14px 12px 40px', fontSize: 14 }} />
            </div>

            <label style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0', display: 'block', marginBottom: 6 }}>Password</label>
            <div style={{ position: 'relative', marginBottom: 22 }}>
              <Lock size={16} color="#7B8DB0" style={{ position: 'absolute', left: 13, top: 13 }} />
              <input className="edu-input" type="password" value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                style={{ width: '100%', padding: '12px 14px 12px 40px', fontSize: 14 }} />
            </div>

            <button className="btn-primary" disabled={loading} style={{ width: '100%', padding: 13, fontSize: 15 }}>
              {loading ? 'Please wait...' : isSignup ? 'Sign Up' : 'Log In'}
            </button>
          </form>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '22px 0' }}>
            <div style={{ height: 1, flex: 1, background: 'rgba(255,255,255,0.08)' }} />
            <span style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0' }}>or</span>
            <div style={{ height: 1, flex: 1, background: 'rgba(255,255,255,0.08)' }} />
          </div>

          <button type="button" onClick={startGoogle}
            style={{ width: '100%', padding: 12, borderRadius: 12, border: '1px solid rgba(255,255,255,0.12)', background: 'rgba(255,255,255,0.05)', color: '#F0F4FF', fontFamily: 'Syne', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <KeyRound size={16} /> Continue with Google
          </button>

          <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', marginTop: 22, textAlign: 'center' }}>
            {isSignup ? 'Already have an account?' : 'Need an account?'}{' '}
            <Link to={isSignup ? '/login' : '/signup'} style={{ color: '#00D4FF', textDecoration: 'none', fontWeight: 700 }}>
              {isSignup ? 'Log in' : 'Sign up'}
            </Link>
          </p>
        </GlassCard>
      </div>
    </div>
  )
}

export default AuthPage
