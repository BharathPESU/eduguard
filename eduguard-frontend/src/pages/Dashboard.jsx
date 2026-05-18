import { useState, useEffect } from 'react'
import { Shield, FileCheck, AlertTriangle, TrendingUp, RefreshCw } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import StatCard from '../components/ui/StatCard'
import { getViolations, getSubmissions } from '../api/client'

const Dashboard = () => {
  const [violations, setViolations] = useState([])
  const [submissions, setSubmissions] = useState([])
  const [tab, setTab] = useState('violations')
  const [loading, setLoading] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [v, s] = await Promise.all([getViolations(), getSubmissions()])
      setViolations(v)
      setSubmissions(s)
    } catch (e) {
      console.error('Dashboard fetch error:', e)
    }
    setLoading(false)
  }

  useEffect(() => {
    const timer = setTimeout(fetchData, 0)
    return () => clearTimeout(timer)
  }, [])

  const criticalCount = violations.filter(v => v.severity === 'critical').length
  const avgScore = submissions.length
    ? Math.round(submissions.reduce((a, s) => a + (s.grading?.score || 0), 0) / submissions.length)
    : 0
  const plagiarismCount = submissions.filter(s => s.security?.plagiarism_suspected).length

  return (
    <div style={{ minHeight: '100vh', background: '#0A0F1E', padding: '100px 24px 60px' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 40 }}>
          <div>
            <h1 style={{ fontFamily: 'Syne', fontSize: 28, fontWeight: 800, color: '#F0F4FF', marginBottom: 8 }}>Teacher Dashboard</h1>
            <p style={{ fontFamily: 'DM Sans', fontSize: 15, color: '#7B8DB0' }}>Real-time monitoring of student activity and safety violations</p>
          </div>
          <button onClick={fetchData} disabled={loading}
            style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px', borderRadius: 12, cursor: 'pointer', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', color: '#00D4FF', fontFamily: 'Syne', fontWeight: 600, fontSize: 14 }}>
            <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            Refresh
          </button>
        </div>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
          <StatCard label="Total Violations" value={violations.length} icon={Shield} accent="#FF3366" />
          <StatCard label="Critical Alerts" value={criticalCount} icon={AlertTriangle} accent="#FFB800" />
          <StatCard label="Exams Graded" value={submissions.length} icon={FileCheck} accent="#00D4FF" />
          <StatCard label="Average Score" value={`${avgScore}%`} icon={TrendingUp} accent="#00FF88" sub={`${plagiarismCount} plagiarism flags`} />
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 24, background: 'rgba(255,255,255,0.03)', padding: 4, borderRadius: 14, border: '1px solid rgba(255,255,255,0.06)', width: 'fit-content' }}>
          {['violations', 'submissions'].map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding: '10px 24px', borderRadius: 10, cursor: 'pointer', border: 'none',
              fontFamily: 'Syne', fontWeight: 600, fontSize: 14,
              background: tab === t ? 'rgba(0,212,255,0.12)' : 'transparent',
              color: tab === t ? '#00D4FF' : '#7B8DB0',
              borderBottom: tab === t ? '2px solid #00D4FF' : '2px solid transparent',
              transition: 'all 0.2s ease',
            }}>
              {t === 'violations' ? `🚨 Violations (${violations.length})` : `📝 Submissions (${submissions.length})`}
            </button>
          ))}
        </div>

        {/* Violations tab */}
        {tab === 'violations' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {violations.length === 0 && (
              <GlassCard accent="none" hover={false}>
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#7B8DB0' }}>
                  <Shield size={36} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                  <p style={{ fontFamily: 'Syne', fontWeight: 600 }}>No violations yet</p>
                  <p style={{ fontFamily: 'DM Sans', fontSize: 13, marginTop: 4 }}>Try sending a jailbreak prompt from the AI Tutor page</p>
                </div>
              </GlassCard>
            )}
            {violations.map((v, i) => (
              <GlassCard key={i} accent={v.severity === 'critical' ? 'danger' : 'flag'} hover={false}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                      <span style={{
                        padding: '3px 10px', borderRadius: 20,
                        background: v.severity === 'critical' ? 'rgba(255,51,102,0.12)' : 'rgba(255,184,0,0.12)',
                        color: v.severity === 'critical' ? '#FF3366' : '#FFB800',
                        border: `1px solid ${v.severity === 'critical' ? 'rgba(255,51,102,0.3)' : 'rgba(255,184,0,0.3)'}`,
                        fontFamily: 'Syne', fontWeight: 700, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em',
                      }}>
                        {v.severity}
                      </span>
                      <span style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: 14, color: '#F0F4FF' }}>{v.type?.replace(/_/g, ' ')}</span>
                    </div>
                    <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', marginBottom: 8 }}>
                      <strong style={{ color: '#F0F4FF' }}>Student:</strong> {v.student_id} &nbsp;·&nbsp;
                      <strong style={{ color: '#F0F4FF' }}>Endpoint:</strong> {v.endpoint}
                    </p>
                    <div style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', background: 'rgba(255,255,255,0.03)', padding: '10px 14px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.06)', fontStyle: 'italic' }}>
                      "{v.input?.slice(0, 120)}{v.input?.length > 120 ? '...' : ''}"
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <p style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0' }}>
                      {v.timestamp ? new Date(v.timestamp).toLocaleTimeString() : 'just now'}
                    </p>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        )}

        {/* Submissions tab */}
        {tab === 'submissions' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {submissions.length === 0 && (
              <GlassCard accent="none" hover={false}>
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#7B8DB0' }}>
                  <FileCheck size={36} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                  <p style={{ fontFamily: 'Syne', fontWeight: 600 }}>No submissions yet</p>
                  <p style={{ fontFamily: 'DM Sans', fontSize: 13, marginTop: 4 }}>Submit an exam answer from the Exam Validator page</p>
                </div>
              </GlassCard>
            )}
            {submissions.map((s, i) => {
              const grading = s.grading || {}
              const security = s.security || {}
              const gradeColors = { A: '#00FF88', B: '#00D4FF', C: '#FFB800', D: '#FF8800', F: '#FF3366' }
              const gc = gradeColors[grading.grade] || '#7B8DB0'

              return (
                <GlassCard key={i} accent={security.plagiarism_suspected ? 'flag' : 'safe'} hover={false}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                        <div style={{ width: 36, height: 36, borderRadius: '50%', background: gc + '18', border: `2px solid ${gc}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <span style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 14, color: gc }}>{grading.grade}</span>
                        </div>
                        <div>
                          <p style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 15, color: '#F0F4FF' }}>
                            {s.student_id} · {s.exam_id}
                          </p>
                          <p style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0' }}>Score: {grading.score}/100</p>
                        </div>
                        {security.plagiarism_suspected && (
                          <span style={{ padding: '3px 10px', borderRadius: 20, background: 'rgba(255,184,0,0.1)', color: '#FFB800', border: '1px solid rgba(255,184,0,0.3)', fontFamily: 'Syne', fontWeight: 700, fontSize: 11 }}>
                            ⚠️ PLAGIARISM
                          </span>
                        )}
                      </div>
                      <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', lineHeight: 1.6 }}>
                        {grading.feedback?.slice(0, 120)}...
                      </p>
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <p style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0' }}>
                        AI Gen: {security.ai_generated_probability ?? 0}%
                      </p>
                      <p style={{ fontFamily: 'DM Sans', fontSize: 11, color: '#7B8DB066', marginTop: 4 }}>
                        {s.timestamp ? new Date(s.timestamp).toLocaleDateString() : 'today'}
                      </p>
                    </div>
                  </div>
                </GlassCard>
              )
            })}
          </div>
        )}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

export default Dashboard
