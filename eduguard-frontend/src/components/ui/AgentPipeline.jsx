/**
 * AgentPipeline — fullscreen overlay that animates the 3-agent
 * extraction pipeline while a PYQ paper is being processed.
 *
 * Props:
 *   stage  0 = Agent1 running, 1 = Agent2 running, 2 = Agent3 running, 3 = done
 *   total  number of questions extracted (shown when done)
 */
const AGENTS = [
  {
    id: 1,
    name: 'Vision Extractor',
    role: 'Agent 1',
    icon: '🔍',
    color: '#00D4FF',
    glow: 'rgba(0,212,255,0.3)',
    border: 'rgba(0,212,255,0.4)',
    bg: 'rgba(0,212,255,0.07)',
    tasks: [
      'Reading document structure…',
      'Converting pages to images…',
      'Scanning for question patterns…',
      'Analysing marks allocation…',
    ],
  },
  {
    id: 2,
    name: 'Session Manager',
    role: 'Agent 2',
    icon: '🗂️',
    color: '#FFB800',
    glow: 'rgba(255,184,0,0.3)',
    border: 'rgba(255,184,0,0.4)',
    bg: 'rgba(255,184,0,0.07)',
    tasks: [
      'Organising extracted questions…',
      'Building session index…',
      'Persisting session to disk…',
    ],
  },
  {
    id: 3,
    name: 'AI Answer Engine',
    role: 'Agent 3',
    icon: '✨',
    color: '#8B5CF6',
    glow: 'rgba(139,92,246,0.3)',
    border: 'rgba(139,92,246,0.4)',
    bg: 'rgba(139,92,246,0.07)',
    tasks: [
      'Loading Llama 3.3 70B model…',
      'Priming academic tutor context…',
      'Ready to generate answers…',
    ],
  },
]

import { useEffect, useState } from 'react'

export default function AgentPipeline({ stage, total }) {
  const [tick, setTick] = useState(0)

  // Cycle through sub-tasks for the active agent
  useEffect(() => {
    const t = setInterval(() => setTick(p => p + 1), 1800)
    return () => clearInterval(t)
  }, [stage])

  const done = stage >= 3

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 999,
      background: 'rgba(5,8,20,0.94)',
      backdropFilter: 'blur(18px)',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 0,
    }}>
      <style>{`
        @keyframes spin360  { to { transform: rotate(360deg); } }
        @keyframes pulseRing { 0%,100% { transform: scale(1); opacity:.6 } 50% { transform: scale(1.18); opacity:1 } }
        @keyframes slideUp   { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
        @keyframes beam      { 0%,100% { opacity:.15 } 50% { opacity:1 } }
        @keyframes progressAnim { from { width:0 } }
        @keyframes checkPop  { 0% { transform:scale(0) rotate(-20deg); opacity:0 } 70% { transform:scale(1.2); } 100% { transform:scale(1); opacity:1 } }
        @keyframes starBurst { 0% { transform:scale(0) rotate(0); opacity:0 } 60% { transform:scale(1.3) rotate(10deg); } 100% { transform:scale(1) rotate(0); opacity:1 } }
        @keyframes connectorFlow { 0%{ background-position:0 0 } 100%{ background-position:0 40px } }
      `}</style>

      {/* Title */}
      <div style={{ textAlign:'center', marginBottom: 40 }}>
        {done ? (
          <div style={{ animation: 'starBurst 0.5s ease' }}>
            <div style={{ fontSize: 52, marginBottom: 8 }}>🎉</div>
            <h2 style={{ fontFamily:'Syne', fontSize:26, fontWeight:800, color:'#00FF88', margin:0 }}>
              Pipeline Complete!
            </h2>
            <p style={{ fontFamily:'DM Sans', fontSize:15, color:'#7B8DB0', margin:'8px 0 0' }}>
              {total > 0 ? `${total} questions extracted and ready` : 'Session ready for practice'}
            </p>
          </div>
        ) : (
          <>
            <h2 style={{ fontFamily:'Syne', fontSize:22, fontWeight:800, color:'#F0F4FF', margin:0 }}>
              EduGuard Pipeline
            </h2>
            <p style={{ fontFamily:'DM Sans', fontSize:13, color:'#7B8DB0', margin:'6px 0 0' }}>
              Multi-agent extraction in progress…
            </p>
          </>
        )}
      </div>

      {/* Agent cards */}
      <div style={{ display:'flex', flexDirection:'column', gap: 0, width:'100%', maxWidth: 520 }}>
        {AGENTS.map((agent, idx) => {
          const isActive = stage === idx
          const isDone   = stage > idx
          const isPending = stage < idx

          return (
            <div key={agent.id}>
              {/* Agent card */}
              <div style={{
                display:'flex', alignItems:'flex-start', gap:16,
                padding:'20px 24px',
                borderRadius: 16,
                background: isActive ? agent.bg : isDone ? 'rgba(0,255,136,0.04)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isActive ? agent.border : isDone ? 'rgba(0,255,136,0.2)' : 'rgba(255,255,255,0.06)'}`,
                boxShadow: isActive ? `0 0 30px ${agent.glow}` : 'none',
                transition: 'all 0.4s ease',
                animation: isActive ? 'slideUp 0.35s ease' : 'none',
              }}>
                {/* Icon / spinner */}
                <div style={{ flexShrink: 0, width:46, height:46, position:'relative' }}>
                  {isActive && (
                    <div style={{
                      position:'absolute', inset:-4, borderRadius:'50%',
                      border: `2px solid ${agent.color}`,
                      borderTopColor:'transparent',
                      animation: 'spin360 0.9s linear infinite',
                    }} />
                  )}
                  <div style={{
                    width:46, height:46, borderRadius:'50%',
                    background: isDone ? 'rgba(0,255,136,0.15)' : isActive ? agent.bg : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${isDone ? 'rgba(0,255,136,0.4)' : isActive ? agent.border : 'rgba(255,255,255,0.08)'}`,
                    display:'flex', alignItems:'center', justifyContent:'center',
                    fontSize: 20,
                    animation: isActive ? 'pulseRing 1.6s ease infinite' : 'none',
                  }}>
                    {isDone ? '✅' : agent.icon}
                  </div>
                </div>

                {/* Text */}
                <div style={{ flex:1 }}>
                  <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:4 }}>
                    <span style={{
                      fontFamily:'Syne', fontWeight:800, fontSize:14,
                      color: isDone ? '#00FF88' : isActive ? agent.color : '#4B5A7A',
                    }}>
                      {agent.role}
                    </span>
                    <span style={{
                      fontFamily:'DM Sans', fontSize:13, fontWeight:600,
                      color: isPending ? '#4B5A7A' : '#F0F4FF',
                    }}>
                      {agent.name}
                    </span>
                    {isDone && (
                      <span style={{
                        padding:'2px 8px', borderRadius:20,
                        background:'rgba(0,255,136,0.12)', color:'#00FF88',
                        fontFamily:'Syne', fontWeight:700, fontSize:10,
                        animation: 'checkPop 0.4s ease',
                      }}>DONE</span>
                    )}
                    {isPending && (
                      <span style={{
                        padding:'2px 8px', borderRadius:20,
                        background:'rgba(255,255,255,0.04)', color:'#4B5A7A',
                        fontFamily:'Syne', fontWeight:700, fontSize:10,
                      }}>WAITING</span>
                    )}
                  </div>

                  {/* Active sub-task ticker */}
                  {isActive && (
                    <p style={{
                      fontFamily:'DM Sans', fontSize:13, color: agent.color,
                      margin:0, animation:'slideUp 0.3s ease',
                      key: tick,
                    }}>
                      {agent.tasks[tick % agent.tasks.length]}
                    </p>
                  )}
                  {isDone && (
                    <p style={{ fontFamily:'DM Sans', fontSize:13, color:'#00FF88', margin:0 }}>
                      Completed successfully
                    </p>
                  )}
                  {isPending && (
                    <p style={{ fontFamily:'DM Sans', fontSize:13, color:'#4B5A7A', margin:0 }}>
                      Waiting for previous agent…
                    </p>
                  )}

                  {/* Progress bar (active only) */}
                  {isActive && (
                    <div style={{ marginTop:10, height:3, borderRadius:2, background:'rgba(255,255,255,0.07)' }}>
                      <div style={{
                        height:'100%', borderRadius:2,
                        background: `linear-gradient(90deg, ${agent.color}88, ${agent.color})`,
                        animation: 'progressAnim 3s ease-out forwards, beam 1.5s ease-in-out infinite',
                        width:'85%',
                      }} />
                    </div>
                  )}
                </div>
              </div>

              {/* Connector between agents */}
              {idx < AGENTS.length - 1 && (
                <div style={{
                  width:2, height:20, margin:'0 auto',
                  background: stage > idx
                    ? 'linear-gradient(180deg,#00FF88,rgba(0,255,136,0.2))'
                    : 'rgba(255,255,255,0.07)',
                  transition: 'background 0.5s ease',
                }} />
              )}
            </div>
          )
        })}
      </div>

      {/* Overall progress dots */}
      {!done && (
        <div style={{ display:'flex', gap:8, marginTop:32 }}>
          {[0,1,2].map(i => (
            <div key={i} style={{
              width: i === stage ? 24 : 8, height:8, borderRadius:4,
              background: i < stage ? '#00FF88' : i === stage ? AGENTS[i].color : 'rgba(255,255,255,0.1)',
              transition:'all 0.4s ease',
              boxShadow: i === stage ? `0 0 10px ${AGENTS[stage]?.glow}` : 'none',
            }} />
          ))}
        </div>
      )}
    </div>
  )
}
