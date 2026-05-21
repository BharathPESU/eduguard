import { useEffect, useRef, useState } from 'react'
import { BookOpen, History, Upload, Trash2, Grid, ChevronRight, ChevronLeft, Sparkles, FileText, BarChart2 } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import AgentPipeline from '../components/ui/AgentPipeline'
import toast from 'react-hot-toast'
import { pyqUpload, pyqGetSessions, pyqGetSessionDetail, pyqGetQuestion, pyqGetAnswer, pyqDeleteSession } from '../api/client'

const P = '#8B5CF6'
const P2 = 'rgba(139,92,246,0.12)'
const P3 = 'rgba(139,92,246,0.25)'

// ── Simple inline markdown renderer ──────────────────────
function renderMd(text) {
  if (!text) return []
  const lines = text.split('\n')
  return lines.map((line, i) => {
    if (/^###\s/.test(line)) return <h4 key={i} style={{ fontFamily: 'Syne', color: '#00FF88', fontSize: 15, margin: '14px 0 4px' }}>{line.replace(/^###\s/, '')}</h4>
    if (/^##\s/.test(line)) return <h3 key={i} style={{ fontFamily: 'Syne', color: P, fontSize: 17, margin: '18px 0 6px' }}>{line.replace(/^##\s/, '')}</h3>
    if (/^#\s/.test(line)) return <h2 key={i} style={{ fontFamily: 'Syne', color: P, fontSize: 20, margin: '20px 0 8px' }}>{line.replace(/^#\s/, '')}</h2>
    if (/^[-*]\s/.test(line)) return <li key={i} style={{ fontFamily: 'DM Sans', color: '#D0D8F0', fontSize: 14, lineHeight: 1.7, marginLeft: 18, marginBottom: 3 }}>{inlineMd(line.replace(/^[-*]\s/, ''))}</li>
    if (/^\d+\.\s/.test(line)) return <li key={i} style={{ fontFamily: 'DM Sans', color: '#D0D8F0', fontSize: 14, lineHeight: 1.7, marginLeft: 18, marginBottom: 3 }}>{inlineMd(line.replace(/^\d+\.\s/, ''))}</li>
    if (line.trim() === '') return <br key={i} />
    return <p key={i} style={{ fontFamily: 'DM Sans', color: '#D0D8F0', fontSize: 14, lineHeight: 1.75, margin: '3px 0' }}>{inlineMd(line)}</p>
  })
}

function inlineMd(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/)
  return parts.map((p, i) => {
    if (/^\*\*/.test(p)) return <strong key={i} style={{ color: '#00FF88' }}>{p.replace(/\*\*/g, '')}</strong>
    if (/^`/.test(p)) return <code key={i} style={{ background: 'rgba(0,0,0,0.4)', color: '#00D4FF', padding: '1px 6px', borderRadius: 4, fontSize: 13 }}>{p.replace(/`/g, '')}</code>
    return p
  })
}

export default function PYQPage() {
  const fileRef = useRef(null)
  const [fileName, setFileName] = useState('')
  const [subject, setSubject] = useState('')
  const [year, setYear] = useState('')
  const [uploadLoading, setUploadLoading] = useState(false)
  const [pipelineStage, setPipelineStage] = useState(-1)   // -1 = hidden
  const [extractedTotal, setExtractedTotal] = useState(0)

  const [sessions, setSessions] = useState([])
  const [selectedSession, setSelectedSession] = useState(null)

  const [currentQNum, setCurrentQNum] = useState(1)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [currentAnswer, setCurrentAnswer] = useState(null)
  const [answeredQs, setAnsweredQs] = useState(new Set())

  const [questionLoading, setQuestionLoading] = useState(false)
  const [answerLoading, setAnswerLoading] = useState(false)
  const [cachedAnswers, setCachedAnswers] = useState({})  // {question_number: answer_obj}

  useEffect(() => { loadSessions() }, [])

  async function loadSessions() {
    try { const d = await pyqGetSessions(); setSessions(d.sessions || []) }
    catch { /* silently ignore */ }
  }

  async function handleUpload() {
    const file = fileRef.current?.files[0]
    if (!file) return toast.error('Select a file first')
    const fd = new FormData()
    fd.append('file', file)
    fd.append('subject', subject || 'Unknown')
    fd.append('year', year || 'Unknown')

    // ── Start pipeline animation ──
    setPipelineStage(0)   // Agent 1 active
    setUploadLoading(true)

    // Stage timers: Agent 2 fires after ~18 s, Agent 3 after ~24 s
    // (real extraction takes 20-45 s; timers are cosmetic hints)
    const t1 = setTimeout(() => setPipelineStage(1), 18000)
    const t2 = setTimeout(() => setPipelineStage(2), 24000)

    try {
      const d = await pyqUpload(fd)
      clearTimeout(t1); clearTimeout(t2)
      setExtractedTotal(d.session.total_questions)
      setPipelineStage(3)   // Done
      await new Promise(r => setTimeout(r, 1600))  // Show ✅ briefly
      toast.success(`Extracted ${d.session.total_questions} questions!`)
      await loadSessions()
      await selectSession(d.session)
    } catch (e) {
      clearTimeout(t1); clearTimeout(t2)
      toast.error('Upload failed: ' + (e.response?.data?.detail || e.message))
    }

    setPipelineStage(-1)
    setUploadLoading(false)
    setFileName('')
    if (fileRef.current) fileRef.current.value = ''
  }

  async function selectSession(s) {
    setSelectedSession(s)
    setCurrentQNum(1)
    setCurrentAnswer(null)
    setAnsweredQs(new Set())
    setCachedAnswers({})

    try {
      // One call: gets all questions + all cached answers from MongoDB
      const detail = await pyqGetSessionDetail(s.session_id)

      // Build normalised cache map: {qNum (int) -> {answer, model_used, from_cache}}
      const cache = {}
      Object.entries(detail.cached_answers || {}).forEach(([k, v]) => {
        const num = parseInt(k)
        // v may be a string (old format) or object (new format)
        cache[num] = typeof v === 'string' ? { answer: v, model_used: '', from_cache: true } : { ...v, from_cache: true }
      })
      setCachedAnswers(cache)
      setAnsweredQs(new Set(Object.keys(cache).map(Number)))

      // Store questions list on selectedSession so we don't need a separate /question call
      const sessionWithQs = { ...s, questions: detail.questions || [] }
      setSelectedSession(sessionWithQs)

      // Show Q1 immediately from local data (no extra API call needed)
      const q1 = (detail.questions || [])[0]
      if (q1) setCurrentQuestion({ question: q1, subject: detail.subject, year: detail.year,
        current_question_number: 1, total_questions: detail.total_questions, is_last: detail.total_questions === 1 })
      if (cache[1]) setCurrentAnswer(cache[1])
    } catch (e) {
      toast.error('Failed to load session: ' + (e.response?.data?.detail || e.message))
    }
  }

  async function loadQuestion(sessionId, num) {
    // First: show from local cache instantly (zero latency)
    setCachedAnswers(prev => {
      if (prev[num]) setCurrentAnswer(prev[num])
      else setCurrentAnswer(null)
      return prev
    })

    // Use locally stored questions if available (avoid API call)
    const localQs = selectedSession?.questions || []
    if (localQs.length >= num) {
      const q = localQs[num - 1]
      setCurrentQuestion({
        question: q, subject: selectedSession.subject, year: selectedSession.year,
        current_question_number: num,
        total_questions: selectedSession.total_questions,
        is_last: num === selectedSession.total_questions,
      })
      setQuestionLoading(false)
      return
    }

    // Fallback: fetch from API
    setQuestionLoading(true)
    try {
      const d = await pyqGetQuestion(sessionId, num)
      setCurrentQuestion(d)
      if (d.cached_answer) {
        const ans = { ...d.cached_answer, from_cache: true }
        setCurrentAnswer(ans)
        setAnsweredQs(prev => new Set([...prev, num]))
        setCachedAnswers(prev => ({ ...prev, [num]: ans }))
      }
    } catch (e) {
      toast.error('Failed to load question: ' + (e.response?.data?.detail || e.message))
    }
    setQuestionLoading(false)
  }

  async function handleGetAnswer() {
    if (!selectedSession || !currentQuestion) return
    // Already cached locally — show instantly, no API call
    if (cachedAnswers[currentQNum]) {
      setCurrentAnswer({ ...cachedAnswers[currentQNum], from_cache: true })
      setAnsweredQs(prev => new Set([...prev, currentQNum]))
      return
    }
    setAnswerLoading(true)
    try {
      const d = await pyqGetAnswer(selectedSession.session_id, currentQNum)
      // d.answer is the text; store full object in cache
      const ansObj = { answer: d.answer, model_used: d.model_used || '', from_cache: d.from_cache || false }
      setCurrentAnswer(ansObj)
      setAnsweredQs(prev => new Set([...prev, currentQNum]))
      setCachedAnswers(prev => ({ ...prev, [currentQNum]: ansObj }))
    } catch (e) {
      toast.error('Answer failed: ' + (e.response?.data?.detail || e.message))
    }
    setAnswerLoading(false)
  }

  async function goToQuestion(num) {
    if (!selectedSession || num < 1 || num > selectedSession.total_questions) return
    setCurrentQNum(num)
    await loadQuestion(selectedSession.session_id, num)
  }

  async function handleDelete(sessionId, e) {
    e.stopPropagation()
    try {
      await pyqDeleteSession(sessionId)
      toast.success('Session deleted')
      if (selectedSession?.session_id === sessionId) {
        setSelectedSession(null); setCurrentQuestion(null); setCurrentAnswer(null)
      }
      await loadSessions()
    } catch { toast.error('Delete failed') }
  }

  const total = selectedSession?.total_questions || 0
  const progress = total ? Math.round((answeredQs.size / total) * 100) : 0

  return (
    <div style={{ minHeight: '100vh', background: '#0A0F1E', padding: '80px 16px 40px' }}>
      {/* ── Agent Pipeline Overlay ── */}
      {pipelineStage >= 0 && <AgentPipeline stage={pipelineStage} total={extractedTotal} />}
      <div style={{ maxWidth: 1300, margin: '0 auto', display: 'flex', gap: 20, alignItems: 'flex-start' }}>

        {/* ── LEFT SIDEBAR ── */}
        <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ marginBottom: 4 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <div style={{ width: 38, height: 38, borderRadius: 10, background: P2, border: `1px solid ${P3}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <BookOpen size={18} color={P} />
              </div>
              <h1 style={{ fontFamily: 'Syne', fontSize: 22, fontWeight: 800, color: '#F0F4FF', margin: 0 }}>PYQ Practice</h1>
            </div>
            <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', margin: 0 }}>Upload question papers, practice with AI</p>
          </div>

          {/* Upload Card */}
          <GlassCard accent="purple" hover={false}>
            <h3 style={{ fontFamily: 'Syne', fontSize: 12, fontWeight: 700, color: '#7B8DB0', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>Upload Paper</h3>
            <input ref={fileRef} type="file" accept=".pdf,.png,.jpg,.jpeg" style={{ display: 'none' }}
              onChange={e => setFileName(e.target.files[0]?.name || '')} />
            <button onClick={() => fileRef.current?.click()}
              style={{ width: '100%', padding: '10px 14px', borderRadius: 10, border: `1px dashed ${P3}`, background: P2, color: P, fontFamily: 'Syne', fontWeight: 700, fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 8 }}>
              <Upload size={15} /> Choose File
            </button>
            {fileName && <p style={{ fontFamily: 'DM Sans', fontSize: 11, color: '#7B8DB0', marginBottom: 10, wordBreak: 'break-all' }}>{fileName}</p>}

            <input className="edu-input" placeholder="Subject (e.g. Physics)" value={subject} onChange={e => setSubject(e.target.value)}
              style={{ width: '100%', padding: '9px 12px', fontSize: 13, marginBottom: 8 }} />
            <input className="edu-input" placeholder="Year (e.g. 2023)" value={year} onChange={e => setYear(e.target.value)}
              style={{ width: '100%', padding: '9px 12px', fontSize: 13, marginBottom: 14 }} />

            <button onClick={handleUpload} disabled={uploadLoading}
              style={{ width: '100%', padding: '11px', borderRadius: 10, border: 'none', background: uploadLoading ? 'rgba(139,92,246,0.4)' : `linear-gradient(135deg, #7C3AED, ${P})`, color: 'white', fontFamily: 'Syne', fontWeight: 700, fontSize: 14, cursor: uploadLoading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              {uploadLoading ? <><span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</span> Extracting…</> : <><Sparkles size={15} /> Upload & Extract</>}
            </button>
          </GlassCard>

          {/* Session History */}
          <GlassCard accent="none" hover={false}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <History size={15} color={P} />
              <h3 style={{ fontFamily: 'Syne', fontSize: 12, fontWeight: 700, color: '#7B8DB0', textTransform: 'uppercase', letterSpacing: '0.08em', margin: 0 }}>Previous Papers</h3>
            </div>
            {sessions.length === 0
              ? <p style={{ fontFamily: 'DM Sans', fontSize: 13, color: '#7B8DB0', textAlign: 'center', padding: '16px 0' }}>No papers uploaded yet</p>
              : <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 320, overflowY: 'auto' }}>
                {sessions.map(s => (
                  <div key={s.session_id} onClick={() => selectSession(s)}
                    style={{ padding: '10px 12px', borderRadius: 10, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, background: selectedSession?.session_id === s.session_id ? P2 : 'rgba(255,255,255,0.03)', border: `1px solid ${selectedSession?.session_id === s.session_id ? P3 : 'rgba(255,255,255,0.07)'}`, transition: 'all 0.15s' }}>
                    <FileText size={14} color={P} style={{ flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontFamily: 'Syne', fontSize: 12, fontWeight: 700, color: '#F0F4FF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', margin: 0 }}>{s.filename}</p>
                      <p style={{ fontFamily: 'DM Sans', fontSize: 11, color: '#7B8DB0', margin: '2px 0 0' }}>{s.subject} · {s.year} · {s.total_questions}Q</p>
                    </div>
                    <button onClick={e => handleDelete(s.session_id, e)} style={{ background: 'none', border: 'none', color: '#FF3366', cursor: 'pointer', padding: 2, flexShrink: 0 }}>
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))}
              </div>}
          </GlassCard>
        </div>

        {/* ── CENTER ── */}
        <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {!selectedSession ? (
            <GlassCard accent="purple" hover={false} style={{ textAlign: 'center', padding: '80px 40px' }}>
              <Upload size={52} color={P} style={{ opacity: 0.35, margin: '0 auto 16px' }} />
              <p style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 18, color: '#F0F4FF', marginBottom: 8 }}>Upload a question paper to start practicing</p>
              <p style={{ fontFamily: 'DM Sans', fontSize: 14, color: '#7B8DB0', marginBottom: 24 }}>Supports PDF, PNG, and JPG question papers</p>
              <button onClick={() => fileRef.current?.click()}
                style={{ padding: '12px 28px', borderRadius: 12, border: 'none', background: `linear-gradient(135deg, #7C3AED, ${P})`, color: 'white', fontFamily: 'Syne', fontWeight: 700, fontSize: 15, cursor: 'pointer' }}>
                Upload Paper →
              </button>
            </GlassCard>
          ) : (
            <>
              {/* Session Info Bar */}
              <GlassCard accent="purple" hover={false} style={{ padding: '16px 20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 10 }}>
                  <div>
                    <p style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 14, color: '#F0F4FF', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 340 }}>{selectedSession.filename}</p>
                    <p style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0', margin: '2px 0 0' }}>{selectedSession.subject} · {selectedSession.year}</p>
                  </div>
                  <span style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 18, color: P, whiteSpace: 'nowrap' }}>
                    Q{currentQNum} / {total}
                  </span>
                </div>
                <div style={{ height: 5, borderRadius: 4, background: 'rgba(255,255,255,0.07)' }}>
                  <div style={{ height: '100%', borderRadius: 4, background: `linear-gradient(90deg, #7C3AED, ${P})`, width: `${progress}%`, transition: 'width 0.4s ease' }} />
                </div>
                <p style={{ fontFamily: 'DM Sans', fontSize: 11, color: '#7B8DB0', margin: '5px 0 0' }}>{answeredQs.size} of {total} answered ({progress}%)</p>
              </GlassCard>

              {/* Question Card */}
              <GlassCard accent="purple" hover={false}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                  <span style={{ padding: '4px 12px', borderRadius: 20, background: P2, border: `1px solid ${P3}`, fontFamily: 'Syne', fontWeight: 700, fontSize: 12, color: P }}>
                    Question {currentQNum}
                  </span>
                  {currentQuestion?.question?.marks && (
                    <span style={{ padding: '4px 10px', borderRadius: 20, background: 'rgba(255,184,0,0.1)', border: '1px solid rgba(255,184,0,0.25)', fontFamily: 'Syne', fontWeight: 700, fontSize: 12, color: '#FFB800' }}>
                      {currentQuestion.question.marks} marks
                    </span>
                  )}
                  {answeredQs.has(currentQNum) && (
                    <span style={{ padding: '4px 10px', borderRadius: 20, background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.25)', fontFamily: 'Syne', fontWeight: 700, fontSize: 12, color: '#00FF88' }}>✓ Answered</span>
                  )}
                </div>

                {questionLoading
                  ? <div style={{ padding: '30px 0', textAlign: 'center', color: P, fontFamily: 'DM Sans', fontSize: 14 }}>
                      <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block', marginRight: 8 }}>⟳</span>Loading question…
                    </div>
                  : <p style={{ fontFamily: 'DM Sans', fontSize: 17, color: '#F0F4FF', lineHeight: 1.85, margin: 0 }}>
                      {currentQuestion?.question?.question_text}
                    </p>}

                {currentQuestion?.question?.subject_hint && (
                  <p style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0', marginTop: 10 }}>
                    Topic hint: <em style={{ color: '#7B8DB0' }}>{currentQuestion.question.subject_hint}</em>
                  </p>
                )}

                <div style={{ display: 'flex', gap: 10, marginTop: 20, flexWrap: 'wrap' }}>
                  <button onClick={() => goToQuestion(currentQNum - 1)} disabled={currentQNum <= 1}
                    style={{ padding: '9px 16px', borderRadius: 10, border: `1px solid ${P3}`, background: 'transparent', color: currentQNum <= 1 ? '#4B5A7A' : P, fontFamily: 'Syne', fontWeight: 700, fontSize: 13, cursor: currentQNum <= 1 ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <ChevronLeft size={15} /> Prev
                  </button>

                  <button onClick={handleGetAnswer} disabled={answerLoading}
                    style={{ flex: 1, padding: '10px 20px', borderRadius: 10, border: 'none', background: answerLoading ? 'rgba(139,92,246,0.4)' : `linear-gradient(135deg, #7C3AED, ${P})`, color: 'white', fontFamily: 'Syne', fontWeight: 700, fontSize: 14, cursor: answerLoading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                    {answerLoading
                      ? <><span style={{ display:'inline-block', animation:'spin 0.8s linear infinite' }}>⟳</span> Agent 3 generating…</>
                      : <><Sparkles size={15} /> Get AI Answer</>}
                  </button>

                  <button onClick={() => goToQuestion(currentQNum + 1)} disabled={currentQNum >= total}
                    style={{ padding: '9px 16px', borderRadius: 10, border: `1px solid ${P3}`, background: 'transparent', color: currentQNum >= total ? '#4B5A7A' : P, fontFamily: 'Syne', fontWeight: 700, fontSize: 13, cursor: currentQNum >= total ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
                    Next <ChevronRight size={15} />
                  </button>
                </div>
              </GlassCard>

              {/* Agent 3 thinking banner */}
              {answerLoading && (
                <div style={{ padding:'20px 24px', borderRadius:16, background:'rgba(139,92,246,0.07)', border:'1px solid rgba(139,92,246,0.3)', boxShadow:'0 0 30px rgba(139,92,246,0.15)', animation:'slideUp 0.3s ease', display:'flex', alignItems:'center', gap:16 }}>
                  <div style={{ position:'relative', width:44, height:44, flexShrink:0 }}>
                    <div style={{ position:'absolute', inset:-4, borderRadius:'50%', border:'2px solid #8B5CF6', borderTopColor:'transparent', animation:'spin 0.85s linear infinite' }} />
                    <div style={{ width:44, height:44, borderRadius:'50%', background:'rgba(139,92,246,0.15)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:20 }}>✨</div>
                  </div>
                  <div>
                    <p style={{ fontFamily:'Syne', fontWeight:800, fontSize:14, color:'#8B5CF6', margin:0 }}>Agent 3 — AI Answer Engine</p>
                    <p style={{ fontFamily:'DM Sans', fontSize:13, color:'#7B8DB0', margin:'3px 0 0' }}>Generating comprehensive exam answer with Llama 3.3 70B…</p>
                    <div style={{ marginTop:8, height:3, borderRadius:2, background:'rgba(255,255,255,0.07)', overflow:'hidden' }}>
                      <div style={{ height:'100%', width:'100%', borderRadius:2, background:'linear-gradient(90deg,rgba(139,92,246,0.4),#8B5CF6,rgba(139,92,246,0.4))', backgroundSize:'200% 100%', animation:'shimmer 1.5s linear infinite' }} />
                    </div>
                  </div>
                </div>
              )}

              {/* Answer Card */}
              {currentAnswer && (
                <GlassCard accent="safe" hover={false} style={{ animation: 'fadeIn 0.35s ease' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
                    <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                      <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 14, color: '#00FF88' }}>AI Answer</span>
                      {currentAnswer.from_cache
                        ? <span style={{ padding:'3px 10px', borderRadius:20, background:'rgba(0,255,136,0.12)', border:'1px solid rgba(0,255,136,0.3)', fontFamily:'Syne', fontWeight:700, fontSize:11, color:'#00FF88' }}>⚡ Cached</span>
                        : <span style={{ padding:'3px 10px', borderRadius:20, background:'rgba(0,212,255,0.08)', border:'1px solid rgba(0,212,255,0.2)', fontFamily:'Syne', fontWeight:700, fontSize:11, color:'#00D4FF' }}>✨ AI Generated</span>
                      }
                    </div>
                    <span style={{ padding: '3px 10px', borderRadius: 20, background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', fontFamily: 'DM Sans', fontSize: 11, color: '#00D4FF' }}>
                      {currentAnswer.model_used || 'meta/llama-3.3-70b-instruct'}
                    </span>
                  </div>
                  <div style={{ background: 'rgba(0,255,136,0.03)', border: '1px solid rgba(0,255,136,0.1)', borderRadius: 12, padding: '16px 20px' }}>
                    {renderMd(currentAnswer.answer)}
                  </div>
                </GlassCard>
              )}
            </>
          )}
        </div>

        {/* ── RIGHT PANEL ── */}
        {selectedSession && (
          <div style={{ width: 260, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Question Navigator */}
            <GlassCard accent="none" hover={false}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Grid size={15} color={P} />
                <h3 style={{ fontFamily: 'Syne', fontSize: 12, fontWeight: 700, color: '#7B8DB0', textTransform: 'uppercase', letterSpacing: '0.08em', margin: 0 }}>Questions</h3>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 6 }}>
                {Array.from({ length: total }, (_, i) => i + 1).map(n => {
                  const isCurrent = n === currentQNum
                  const isCached  = Boolean(cachedAnswers[n])
                  const isDone    = answeredQs.has(n)
                  return (
                    <button key={n} onClick={() => goToQuestion(n)} title={isCached ? 'Answer cached in DB' : isDone ? 'Answered this session' : ''}
                      style={{
                        aspectRatio: '1', borderRadius: 8, cursor: 'pointer', transition: 'all 0.15s',
                        fontFamily: 'Syne', fontWeight: 700, fontSize: 12,
                        border: `1px solid ${isCurrent ? P : isCached ? 'rgba(0,212,255,0.4)' : isDone ? 'rgba(0,255,136,0.35)' : 'rgba(255,255,255,0.1)'}`,
                        background: isCurrent ? P2 : isCached ? 'rgba(0,212,255,0.08)' : isDone ? 'rgba(0,255,136,0.07)' : 'rgba(255,255,255,0.03)',
                        color: isCurrent ? P : isCached ? '#00D4FF' : isDone ? '#00FF88' : '#7B8DB0',
                      }}>
                      {isCached ? '⚡' : n}
                    </button>
                  )
                })}
              </div>
            </GlassCard>

            {/* Stats Card */}
            <GlassCard accent="purple" hover={false}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
                <BarChart2 size={15} color={P} />
                <h3 style={{ fontFamily: 'Syne', fontSize: 12, fontWeight: 700, color: '#7B8DB0', textTransform: 'uppercase', letterSpacing: '0.08em', margin: 0 }}>Session Stats</h3>
              </div>
              {[
                ['Total Questions', total],
                ['Answered', answeredQs.size],
                ['Remaining', total - answeredQs.size],
                ['Subject', selectedSession.subject],
                ['Year', selectedSession.year],
                ['Uploaded', new Date(selectedSession.created_at).toLocaleDateString()],
              ].map(([label, val]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <span style={{ fontFamily: 'DM Sans', fontSize: 12, color: '#7B8DB0' }}>{label}</span>
                  <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 13, color: '#F0F4FF' }}>{val}</span>
                </div>
              ))}
            </GlassCard>
          </div>
        )}
      </div>
      <style>{`
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes fadeIn  { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
      `}</style>
    </div>
  )
}
