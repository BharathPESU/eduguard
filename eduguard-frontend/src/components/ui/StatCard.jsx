const StatCard = ({ label, value, icon: Icon, accent = '#00D4FF', sub }) => (
  <div style={{
    background: 'rgba(255,255,255,0.03)',
    border: `1px solid ${accent}22`,
    borderRadius: 16, padding: '20px 24px',
    transition: 'all 0.3s ease',
  }}
  onMouseEnter={e => {
    e.currentTarget.style.borderColor = accent + '55'
    e.currentTarget.style.boxShadow = `0 0 24px ${accent}18`
    e.currentTarget.style.transform = 'translateY(-2px)'
  }}
  onMouseLeave={e => {
    e.currentTarget.style.borderColor = accent + '22'
    e.currentTarget.style.boxShadow = 'none'
    e.currentTarget.style.transform = 'translateY(0)'
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', marginBottom: 8 }}>{label}</p>
        <p style={{ fontFamily: 'Syne', fontSize: 32, fontWeight: 800, color: accent }}>{value}</p>
        {sub && <p style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB066', marginTop: 4 }}>{sub}</p>}
      </div>
      {Icon && (
        <div style={{
          width: 44, height: 44, borderRadius: 12,
          background: accent + '18', border: `1px solid ${accent}33`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Icon size={20} color={accent} />
        </div>
      )}
    </div>
  </div>
)

export default StatCard