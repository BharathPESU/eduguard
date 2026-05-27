import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('eduguard_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const clearStoredSession = () => {
  localStorage.removeItem('eduguard_access_token')
  localStorage.removeItem('eduguard_refresh_token')
  localStorage.removeItem('eduguard_user_email')
}

const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('eduguard_refresh_token')
  if (!refreshToken) throw new Error('No refresh token available')

  const res = await axios.post(`${API_BASE}/auth/refresh`, {
    refresh_token: refreshToken,
  })

  const accessToken = res.data?.access_token
  if (!accessToken) throw new Error('Refresh response did not include an access token')

  localStorage.setItem('eduguard_access_token', accessToken)
  if (res.data?.session?.refresh_token) {
    localStorage.setItem('eduguard_refresh_token', res.data.session.refresh_token)
  }
  if (res.data?.user?.email) {
    localStorage.setItem('eduguard_user_email', res.data.user.email)
  }

  return accessToken
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const isUnauthorized = error.response?.status === 401
    const isAuthRequest = originalRequest?.url?.startsWith('/auth/')

    if (!isUnauthorized || originalRequest?._retry || isAuthRequest) {
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      const accessToken = await refreshAccessToken()
      originalRequest.headers = originalRequest.headers || {}
      originalRequest.headers.Authorization = `Bearer ${accessToken}`
      return client(originalRequest)
    } catch (refreshError) {
      clearStoredSession()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(refreshError)
    }
  }
)

export const signup = async (payload) => {
  const res = await client.post('/auth/signup', payload)
  return res.data
}

export const login = async (payload) => {
  const res = await client.post('/auth/login', payload)
  return res.data
}

export const getGoogleAuthUrl = () => {
  return `${API_BASE}/auth/google`
}

export const tutorAsk = async (payload) => {
  const res = await client.post('/tutor/ask', payload)
  return res.data
}

export const generateConceptImage = async (payload) => {
  // NVIDIA qwen-image can take ~90 s; allow 3 min to be safe
  const res = await client.post('/images/concept', payload, { timeout: 180000 })
  return res.data
}

export const uploadDocument = async ({ studentId, file }) => {
  const formData = new FormData()
  formData.append('student_id', studentId)
  formData.append('file', file)

  const res = await client.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
  return res.data
}

export const getDocuments = async (studentId) => {
  const res = await client.get('/documents', { params: { student_id: studentId } })
  return res.data
}

export const getDocumentDownloadUrl = (documentId) => {
  return `${API_BASE}/documents/${documentId}/download`
}

export const examValidate = async (payload) => {
  const res = await client.post('/exam/validate', payload)
  return res.data
}

export const getViolations = async () => {
  const res = await client.get('/dashboard/violations')
  return res.data
}

export const getSubmissions = async () => {
  const res = await client.get('/dashboard/submissions')
  return res.data
}

export const getHealth = async () => {
  const res = await client.get('/health')
  return res.data
}

// ── PYQ Practice ──────────────────────────────────────────
export const pyqUpload = async (formData) => {
  const res = await client.post('/pyq/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000, // Vertex AI extraction can take up to ~60s
  })
  return res.data
}

export const pyqGetSessions = async () => {
  const res = await client.get('/pyq/sessions')
  return res.data
}

export const pyqGetSessionDetail = async (sessionId) => {
  // Returns session + cached_answers map {question_number: answer_text}
  const res = await client.get(`/pyq/session/${sessionId}`)
  return res.data
}

export const pyqGetQuestion = async (sessionId, questionNumber) => {
  const res = await client.post('/pyq/question', {
    session_id: sessionId,
    question_number: questionNumber,
  })
  return res.data
}

export const pyqGetAnswer = async (sessionId, questionNumber) => {
  const res = await client.post('/pyq/answer', {
    session_id: sessionId,
    question_number: questionNumber,
  }, { timeout: 90000 }) // AI answer generation can take time
  return res.data
}

export const pyqDeleteSession = async (sessionId) => {
  const res = await client.delete(`/pyq/session/${sessionId}`)
  return res.data
}

export default client
