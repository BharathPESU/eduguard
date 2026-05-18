import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Shield, Menu, X } from 'lucide-react'

const Navbar = () => {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()

  const links = [
    { to: '/', label: 'Home' },
    { to: '/tutor', label: 'AI Tutor' },
    { to: '/exam', label: 'Exam Validator' },
    { to: '/dashboard', label: 'Dashboard' },
  ]

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      background: 'rgba(10, 15, 30, 0.8)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.06)',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #1548B7, #00D4FF)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Shield size={18} color="white" />
          </div>
          <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 18, color: '#F0F4FF' }}>
            Edu<span style={{ color: '#00D4FF' }}>Guard</span>
          </span>
        </Link>

        {/* Desktop links */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }} className="hidden-mobile">
          {links.map(link => (
            <Link key={link.to} to={link.to} style={{
              padding: '8px 16px',
              borderRadius: 10,
              textDecoration: 'none',
              fontFamily: 'DM Sans',
              fontSize: 14,
              fontWeight: 500,
              color: pathname === link.to ? '#00D4FF' : '#7B8DB0',
              background: pathname === link.to ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
              border: pathname === link.to ? '1px solid rgba(0, 212, 255, 0.2)' : '1px solid transparent',
              transition: 'all 0.2s ease',
            }}>
              {link.label}
            </Link>
          ))}
          <Link to="/tutor" style={{
            padding: '8px 20px',
            borderRadius: 10,
            textDecoration: 'none',
            fontFamily: 'Syne',
            fontSize: 14,
            fontWeight: 600,
            color: 'white',
            background: 'linear-gradient(135deg, #1548B7, #00D4FF)',
            marginLeft: 8,
          }}>
            Try Demo
          </Link>
        </div>

        {/* Mobile menu */}
        <button onClick={() => setOpen(!open)} style={{ background: 'none', border: 'none', color: '#F0F4FF', cursor: 'pointer', display: 'none' }} className="mobile-menu-btn">
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {open && (
        <div style={{
          background: 'rgba(10, 15, 30, 0.98)',
          borderTop: '1px solid rgba(255,255,255,0.06)',
          padding: '16px 24px',
          display: 'flex', flexDirection: 'column', gap: 4,
        }}>
          {links.map(link => (
            <Link key={link.to} to={link.to} onClick={() => setOpen(false)} style={{
              padding: '12px 16px', borderRadius: 10, textDecoration: 'none',
              fontFamily: 'DM Sans', fontSize: 15, color: '#F0F4FF',
            }}>
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}

export default Navbar