import { CheckCircle, XCircle, Clock } from 'lucide-react'

const PipelineSteps = ({ stages, blocked_at }) => {
  const allSteps = ['jailbreak_check', 'integrity_check', 'content_safety', 'llm_response']
  const examSteps = ['injection_check', 'plagiarism_detection', 'grading']

  const steps = stages?.includes('jailbreak_check') ? allSteps : examSteps

  const labels = {
    jailbreak_check: 'Jailbreak Scan',
    integrity_check: 'Integrity Check',
    content_safety: 'Content Safety',
    llm_response: 'AI Response',
    injection_check: 'Injection Scan',
    plagiarism_detection: 'Plagiarism AI',
    grading: 'Auto Grader',
  }

  const colors = {
    passed: '#00FF88',
    blocked: '#FF3366',
    pending: '#7B8DB0',
    active: '#00D4FF',
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, flexWrap: 'wrap', rowGap: 12 }}>
      {steps.map((step, i) => {
        const passed = stages?.includes(step)
        const isBlocked = blocked_at === step

        const color = isBlocked ? colors.blocked : passed ? colors.passed : colors.pending
        const Icon = isBlocked ? XCircle : passed ? CheckCircle : Clock

        return (
          <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
              minWidth: 80,
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%',
                background: `${color}18`,
                border: `2px solid ${color}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: passed || isBlocked ? `0 0 12px ${color}44` : 'none',
              }}>
                <Icon size={16} color={color} />
              </div>
              <span style={{ fontFamily: 'DM Sans', fontSize: 10, color, textAlign: 'center', fontWeight: 600 }}>
                {labels[step]}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div style={{
                width: 32, height: 2, marginBottom: 18,
                background: passed ? `linear-gradient(90deg, ${colors.passed}, ${colors.passed}88)` : 'rgba(255,255,255,0.1)',
              }} />
            )}
          </div>
        )
      })}
    </div>
  )
}

export default PipelineSteps
