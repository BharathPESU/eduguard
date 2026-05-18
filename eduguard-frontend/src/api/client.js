import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const tutorAsk = async (payload) => {
  const res = await client.post('/tutor/ask', payload)
  return res.data
}

export const generateConceptImage = async (payload) => {
  const res = await client.post('/images/concept', payload, { timeout: 120000 })
  return res.data
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

export default client
