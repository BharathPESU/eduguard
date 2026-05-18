const GlassCard = ({ children, accent = 'blue', className = '', style = {}, hover = true }) => {
  const accents = {
    blue:   { border: '#00D4FF', glow: 'rgba(0, 212, 255, 0.1)' },
    safe:   { border: '#00FF88', glow: 'rgba(0, 255, 136, 0.1)' },
    danger: { border: '#FF3366', glow: 'rgba(255, 51, 102, 0.1)' },
    flag:   { border: '#FFB800', glow: 'rgba(255, 184, 0, 0.1)' },
    purple: { border: '#8B5CF6', glow: 'rgba(139, 92, 246, 0.1)' },
    none:   { border: 'rgba(255,255,255,0.08)', glow: 'transparent' },
  }

  const { border, glow } = accents[accent] || accents.blue

  return (
    <div
      className={className}
      style={{
        background: 'rgba(255, 255, 255, 0.03)',
        border: `1px solid ${border}22`,
        borderRadius: 16,
        padding: 24,
        backdropFilter: 'blur(12px)',
        transition: hover ? 'all 0.3s ease' : 'none',
        position: 'relative',
        ...style,
      }}
      onMouseEnter={hover ? (e) => {
        e.currentTarget.style.borderColor = border + '55'
        e.currentTarget.style.boxShadow = `0 0 30px ${glow}, 0 8px 32px rgba(0,0,0,0.3)`
        e.currentTarget.style.transform = 'translateY(-2px)'
      } : undefined}
      onMouseLeave={hover ? (e) => {
        e.currentTarget.style.borderColor = border + '22'
        e.currentTarget.style.boxShadow = 'none'
        e.currentTarget.style.transform = 'translateY(0)'
      } : undefined}
    >
      {/* Left accent bar */}
      <div style={{
        position: 'absolute', left: 0, top: '20%', bottom: '20%',
        width: 3, borderRadius: '0 3px 3px 0',
        background: `linear-gradient(180deg, ${border}00, ${border}, ${border}00)`,
      }} />
      {children}
    </div>
  )
}

export default GlassCard