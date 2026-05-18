const StatusBadge = ({ status }) => {
  const config = {
    success: { label: 'PASSED', bg: 'rgba(0,255,136,0.1)', color: '#00FF88', border: '#00FF8844' },
    blocked: { label: 'BLOCKED', bg: 'rgba(255,51,102,0.1)', color: '#FF3366', border: '#FF336644' },
    flagged: { label: 'FLAGGED', bg: 'rgba(255,184,0,0.1)', color: '#FFB800', border: '#FFB80044' },
    loading: { label: 'PROCESSING', bg: 'rgba(0,212,255,0.1)', color: '#00D4FF', border: '#00D4FF44' },
  }

  const c = config[status] || config.loading

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '4px 12px', borderRadius: 20,
      background: c.bg, color: c.color, border: `1px solid ${c.border}`,
      fontFamily: 'Syne', fontWeight: 700, fontSize: 11, letterSpacing: '0.1em',
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: '50%',
        background: c.color,
        boxShadow: `0 0 6px ${c.color}`,
        animation: status === 'loading' ? 'pulse-glow 1s infinite' : 'none',
      }} />
      {c.label}
    </span>
  )
}

export default StatusBadge