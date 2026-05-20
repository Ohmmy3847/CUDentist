import axios from 'axios'
import type { Assessment, DashboardPatient, DashboardStats, Document, IngestStatus, Patient, RagDocument, Symptom, User } from './types'

const BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001/backend'

const client = axios.create({ baseURL: BASE })

client.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (r) => r,
  (err) => {
    // Only treat 401 as session-expired when we're NOT on the login page and NOT calling /auth/login itself
    if (
      err.response?.status === 401 &&
      typeof window !== 'undefined' &&
      window.location.pathname !== '/login' &&
      !err.config?.url?.includes('/auth/login')
    ) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const login = (username: string, password: string, device_token?: string) =>
  client.post<{ access_token?: string; requires_2fa?: boolean; otp_session?: string; device_token?: string }>(
    '/auth/login', { username, password, device_token }
  ).then((r) => r.data)

export const verifyOtp = (otp_session: string, code: string, remember_device?: boolean) =>
  client.post<{ access_token: string; device_token?: string }>(
    '/auth/verify-otp', { otp_session, code, remember_device }
  ).then((r) => r.data)

export const requestChangePassword = (current_password: string, new_password: string) =>
  client.post<{ requires_otp: boolean; otp_session?: string }>('/auth/change-password/request', { current_password, new_password }).then((r) => r.data)

export const confirmChangePassword = (otp_session: string, code: string) =>
  client.post('/auth/change-password/confirm', { otp_session, code })

export const getMe = () => client.get<User>('/auth/me').then((r) => r.data)
export const updateMe = (data: { first_name?: string; last_name?: string; username?: string }) => client.patch<User>('/auth/me', data).then((r) => r.data)

export const requestChangeEmail = (new_email: string) =>
  client.post<{ otp_session: string }>('/auth/change-email/request', { new_email }).then((r) => r.data)

export const confirmChangeEmail = (otp_session: string, code: string) =>
  client.post<User>('/auth/change-email/confirm', { otp_session, code }).then((r) => r.data)

// Dashboard
export const getDashboardStats = () => client.get<DashboardStats>('/dashboard/stats').then((r) => r.data)

export const getDashboardPatients = (params?: {
  risk?: string
  search?: string
  skip?: number
  limit?: number
  status?: string
}) => client.get<{ total: number; patients: DashboardPatient[] }>('/dashboard/patients', { params }).then((r) => r.data)

// Patients
export const listPatients = (params?: { skip?: number; limit?: number }) =>
  client.get<Patient[]>('/patients', { params }).then((r) => r.data)

export const getPatient = (hn: string) => client.get<Patient>(`/patients/${hn}`).then((r) => r.data)

export const createPatient = (data: Partial<Patient>) =>
  client.post<Patient>('/patients', data).then((r) => r.data)

export const updatePatient = (hn: string, data: Partial<Patient>) =>
  client.patch<Patient>(`/patients/${hn}`, data).then((r) => r.data)

export const deletePatient = (hn: string) => client.delete(`/patients/${hn}`)

// Assessments
export const listAssessments = (params?: { patient_hn?: string; skip?: number; limit?: number }) =>
  client.get<Assessment[]>('/assessments', { params }).then((r) => r.data)

export const createAssessment = (data: {
  patient_hn: string
  basic_info?: Record<string, unknown>
  symptom_values?: Record<string, unknown>
  custom_symptoms?: unknown[]
  additional_questions?: string
  language?: string
  submitted_at?: string
}) => client.post<Assessment>('/assessments', data).then((r) => r.data)

export const getAssessment = (id: number) =>
  client.get<Assessment>(`/assessments/${id}`).then((r) => r.data)

export const updateAssessmentResult = (id: number, body: { clinical_summary?: string; qa_answer_text?: string; needs_review?: boolean; confirm_question?: boolean; confirm_custom?: boolean; confirm_conflict?: boolean }) =>
  client.patch<Assessment>(`/assessments/${id}/result`, body).then((r) => r.data)

// Documents
export const listDocuments = (params?: { skip?: number; limit?: number }) =>
  client.get<Document[]>('/documents', { params }).then((r) => r.data)

export const uploadDocument = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return client.post<Document>('/documents', form).then((r) => r.data)
}

export const deleteDocument = (id: number) => client.delete(`/documents/${id}`)

export const updateDocumentStatus = (id: number, rag_status: string) =>
  client.patch<Document>(`/documents/${id}`, { rag_status }).then((r) => r.data)

// RAG admin
export const listRagDocuments = () =>
  client.get<RagDocument[]>('/rag/documents').then(r => r.data)

export const uploadRagDocument = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return client.post<{ filename: string; size: number; status: string }>('/rag/documents', form).then(r => r.data)
}

export const deleteRagDocument = (filename: string) =>
  client.delete(`/rag/documents/${encodeURIComponent(filename)}`)

export const triggerIngest = (mode: 'reingest' | 'append') =>
  client.post('/rag/ingest', { mode }).then(r => r.data)

export const createTextDocument = (filename: string, content: string) =>
  client.post<{ filename: string; size: number; status: string }>('/rag/text-documents', { filename, content }).then(r => r.data)

export const getTextDocument = (filename: string) =>
  client.get<{ filename: string; content: string }>(`/rag/text-documents/${encodeURIComponent(filename)}`).then(r => r.data)

export const updateTextDocument = (filename: string, content: string) =>
  client.put<{ filename: string; size: number; status: string }>(`/rag/text-documents/${encodeURIComponent(filename)}`, { content }).then(r => r.data)

export const getIngestStatus = () =>
  client.get<IngestStatus>('/rag/ingest/status').then(r => r.data)

// Symptoms
export const listSymptoms = () => client.get<Symptom[]>('/symptoms').then((r) => r.data)

export const createSymptom = (data: Partial<Symptom>) =>
  client.post<Symptom>('/symptoms', data).then((r) => r.data)

export const updateSymptom = (id: number, data: Partial<Symptom>) =>
  client.patch<Symptom>(`/symptoms/${id}`, data).then((r) => r.data)

export const deleteSymptom = (id: number) => client.delete(`/symptoms/${id}`)

export const resyncSymptoms = () =>
  client.post<{ status: string; count: number }>('/symptoms/resync').then((r) => r.data)

// Form tokens (patient-facing forms via LINE OA)
export const generateFormToken = (hn: string, scheduleDate?: string) =>
  client.post<{ token: string; url: string; password: string; expires_at: string }>(
    `/patients/${hn}/form-token`,
    null,
    { params: scheduleDate ? { schedule_date: scheduleDate } : {} }
  ).then((r) => r.data)

export const getFormTokens = (hn: string) =>
  client.get<Record<string, { token: string; url: string; password: string }>>(
    `/patients/${hn}/form-tokens`
  ).then((r) => r.data)

// User management (admin)
export const listStaff = () => client.get<{ user_id: number; full_name: string }[]>('/auth/staff').then((r) => r.data)

export const listUsers = () => client.get<User[]>('/auth/users').then((r) => r.data)

export const createUser = (data: { username: string; password: string; first_name: string; last_name: string; email?: string; roles?: string[] }) =>
  client.post<User>('/auth/users', data).then((r) => r.data)

export const updateUser = (user_id: number, data: { first_name?: string; last_name?: string; username?: string; email?: string; password?: string; roles?: string[]; is_active?: boolean }) =>
  client.patch<User>(`/auth/users/${user_id}`, data).then((r) => r.data)

export const deleteUser = (user_id: number) => client.delete(`/auth/users/${user_id}`)

// Account
export const changePassword = (current_password: string, new_password: string) =>
  client.post('/auth/change-password', { current_password, new_password })

export const forgotPassword = (email: string) =>
  client.post('/auth/forgot-password', { email })

export const resetPassword = (token: string, new_password: string) =>
  client.post('/auth/reset-password', { token, new_password })

// Public (no auth) — used by the patient-facing form page
const publicClient = axios.create({ baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001/backend' })

export const checkFormToken = (token: string) =>
  publicClient.get<{ valid: boolean }>(`/public/form/${token}`).then((r) => r.data)

export const unlockPublicForm = (token: string, password: string) =>
  publicClient.post<{
    first_name: string
    last_name: string
    gender: string | null
    date_of_birth: string | null
    phone: string | null
    procedures: string[] | null
    schedule_date: string | null
  }>(`/public/form/${token}/unlock`, { password }).then((r) => r.data)

export const submitPublicForm = (token: string, data: {
  password: string
  basic_info?: Record<string, unknown>
  symptom_values?: Record<string, unknown>
  custom_symptoms?: unknown[]
  additional_questions?: string
  language?: string
  submitted_at?: string
}) => publicClient.post(`/public/form/${token}/submit`, data).then((r) => r.data)
