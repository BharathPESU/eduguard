import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Shield, Zap, BookOpen, BarChart3, ArrowRight } from 'lucide-react'
import NeuralCanvas from '../components/three/NeuralCanvas'
import GlassCard from '../components/ui/GlassCard'
import { getHealth } from '../api/client'

const features = [
  {
    icon: Shield,
    title: 'Multi-Stage Guardrails',
    desc: 'Every student query passes through jailbreak detection, academic integrity checks, and content safety before reaching the LLM.',
    accent: 'blue',
    color: '#00D4FF',
  },
  {
    icon: Zap,
    title: 'Real-Time Blocking',
    desc: 'Cheating prompts, grade injection attacks, and jailbreaks are caught in under 50ms — before the LLM ever sees them.',
    accent: 'danger',
    color: '#FF3366',
  },
  {
    icon: BookOpen,
    title: 'Socratic AI Tutor',
    desc: 'Students get guided hints and Socratic questions — never direct answers. Powered by Claude on AWS Bedrock.',
    accent: 'safe',
    color: '#00FF88',
  },
  {
    icon: BarChart3,
    title: 'Teacher Dashboard',
    desc: 'Real-time violation feed, exam grading panel, plagiarism reports, and per-student risk scoring.',
    accent: 'flag',
    color: '#FFB800',
  },
]

const pipeline = [
  { step: '01', label: 'Student Query', color: '#00D4FF' },
  { step: '02', label: 'Jailbreak Scan', color: '#8B5CF6' },
  { step: '03', label: 'Integrity Check', color: '#FFB800' },
  { step: '04', label: 'Content Safety', color: '#FF3366' },
  { step: '05', label: 'LLM Response', color: '#00FF88' },
]

const Landing = () => {
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    getHealth()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'))
  }, [])

  return (
    <div style={{ minHeight: '100vh', background: '#0A0F1E' }}>
      {/* HERO */}
      <section style={{ position: 'relative', minHeight: '100vh', display: 'flex', alignItems: 'center', overflow: 'hidden' }}>
        <NeuralCanvas />

        {/* Gradient overlays */}
        <div style={{
          position: 'absolute', inset: 0, zIndex: 1,
          background: 'radial-gradient(ellipse at 20% 50%, rgba(21,72,183,0.15) 0%, transparent 60%), radial-gradient(ellipse at 80% 50%, rgba(0,212,255,0.1) 0%, transparent 60%)',
        }} />
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 200, zIndex: 1,
          background: 'linear-gradient(to bottom, transparent, #0A0F1E)',
        }} />

        {/* Hero content */}
        <div style={{ position: 'relative', zIndex: 2, maxWidth: 1200, margin: '0 auto', padding: '120px 24px 80px', textAlign: 'center' }}>
          {/* Status pill */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20, background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.2)', marginBottom: 32 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: apiStatus === 'online' ? '#00FF88' : '#FF3366', boxShadow: `0 0 8px ${apiStatus === 'online' ? '#00FF88' : '#FF3366'}` }} />
            <span style={{ fontFamily: 'DM Sans', fontSize: 13, color: apiStatus === 'online' ? '#00FF88' : '#FF3366', fontWeight: 500 }}>
              API {apiStatus === 'online' ? 'Online' : apiStatus === 'checking' ? 'Checking...' : 'Offline'}
            </span>
          </div>

          <h1 style={{ fontFamily: 'Syne', fontSize: 'clamp(40px, 7vw, 80px)', fontWeight: 800, lineHeight: 1.1, marginBottom: 24, color: '#F0F4FF' }}>
            AI Safety Platform<br />
            <span style={{
              background: 'linear-gradient(135deg, #00D4FF 0%, #1548B7 50%, #00FF88 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              Built for Education
            </span>
          </h1>

          <p style={{ fontFamily: 'DM Sans', fontSize: 'clamp(16px, 2.5vw, 20px)', color: '#7B8DB0', maxWidth: 640, margin: '0 auto 48px', lineHeight: 1.7 }}>
            Multi-stage guardrails that block cheating, jailbreaks, and grade injection before
            they ever reach your LLM. Powered by Mozilla.ai and AWS Bedrock.
          </p>

          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/tutor" style={{
              padding: '14px 32px', borderRadius: 12, textDecoration: 'none',
              fontFamily: 'Syne', fontWeight: 700, fontSize: 15, color: 'white',
              background: 'linear-gradient(135deg, #1548B7, #00D4FF)',
              boxShadow: '0 8px 32px rgba(0,212,255,0.25)',
              display: 'flex', alignItems: 'center', gap: 8,
            }}>
              Try AI Tutor <ArrowRight size={16} />
            </Link>
            <Link to="/exam" style={{
              padding: '14px 32px', borderRadius: 12, textDecoration: 'none',
              fontFamily: 'Syne', fontWeight: 600, fontSize: 15, color: '#F0F4FF',
              background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)',
            }}>
              Exam Validator
            </Link>
          </div>

          {/* Pipeline preview */}
          <div style={{ marginTop: 80, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 0, flexWrap: 'wrap', rowGap: 16 }}>
            {pipeline.map((p, i) => (
              <div key={p.step} style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{
                  padding: '10px 20px', borderRadius: 10,
                  background: `${p.color}12`, border: `1px solid ${p.color}33`,
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
                  minWidth: 100,
                }}>
                  <span style={{ fontFamily: 'Syne', fontSize: 11, color: p.color, fontWeight: 700, opacity: 0.6 }}>{p.step}</span>
                  <span style={{ fontFamily: 'DM Sans', fontSize: 12, color: p.color, fontWeight: 600 }}>{p.label}</span>
                </div>
                {i < pipeline.length - 1 && (
                  <div style={{ width: 24, height: 2, background: `linear-gradient(90deg, ${p.color}44, ${pipeline[i+1].color}44)` }} />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section style={{ padding: '80px 24px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <h2 style={{ fontFamily: 'Syne', fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 800, color: '#F0F4FF', marginBottom: 16 }}>
            Everything you need to deploy AI safely
          </h2>
          <p style={{ fontFamily: 'DM Sans', fontSize: 16, color: '#7B8DB0', maxWidth: 480, margin: '0 auto' }}>
            A production-grade safety layer between your students and your LLM
          </p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
          {features.map(f => (
            <GlassCard key={f.title} accent={f.accent}>
              <div style={{ width: 44, height: 44, borderRadius: 12, background: f.color + '18', border: `1px solid ${f.color}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
                <f.icon size={20} color={f.color} />
              </div>
              <h3 style={{ fontFamily: 'Syne', fontSize: 18, fontWeight: 700, color: '#F0F4FF', marginBottom: 10 }}>{f.title}</h3>
              <p style={{ fontFamily: 'DM Sans', fontSize: 14, color: '#7B8DB0', lineHeight: 1.7 }}>{f.desc}</p>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '80px 24px', textAlign: 'center' }}>
        <div style={{
          maxWidth: 700, margin: '0 auto', padding: '60px 40px',
          background: 'linear-gradient(135deg, rgba(21,72,183,0.15), rgba(0,212,255,0.08))',
          border: '1px solid rgba(0,212,255,0.2)',
          borderRadius: 24,
        }}>
          <h2 style={{ fontFamily: 'Syne', fontSize: 36, fontWeight: 800, color: '#F0F4FF', marginBottom: 16 }}>
            Ready to secure your classroom?
          </h2>
          <p style={{ fontFamily: 'DM Sans', fontSize: 16, color: '#7B8DB0', marginBottom: 32 }}>
            Try the live demo — no signup required
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/tutor" style={{ padding: '12px 28px', borderRadius: 12, textDecoration: 'none', fontFamily: 'Syne', fontWeight: 700, fontSize: 14, color: 'white', background: 'linear-gradient(135deg, #1548B7, #00D4FF)' }}>
              Student Tutor →
            </Link>
            <Link to="/dashboard" style={{ padding: '12px 28px', borderRadius: 12, textDecoration: 'none', fontFamily: 'Syne', fontWeight: 600, fontSize: 14, color: '#F0F4FF', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)' }}>
              Teacher Dashboard →
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Landing
