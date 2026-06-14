export interface User {
  user_id: number
  username: string
  first_name: string
  last_name: string
  email: string | null
  roles: string[]
  is_active: boolean
  is_superuser: boolean
}

export interface PatientExtraInfo {
  surgery_date?: string | null
  discharge_date?: string | null
  note?: string | null
  imf_wire?: boolean
  imf_wire_loops?: number | null
  imf_elastic?: boolean
  imf_elastic_loops?: number | null
  special_icbg?: boolean
  special_icbg_description?: string | null
  special_ng_tube?: boolean
  special_ng_tube_description?: string | null
  lefort_sub_options?: string[]
  bssro_sub_options?: string[]
  biopsy_sub_options?: string[]
  surgical_tooth_numbers?: string | null
  extraction_tooth_numbers?: string | null
}

export interface Patient {
  hn: string
  first_name: string
  last_name: string
  gender: string | null
  date_of_birth: string | null
  phone: string | null
  procedures: string[] | null
  follow_up_date: string | null
  follow_up_schedules?: string[] | null
  responsible_person?: string | null
  responsible_user_id?: number | null
  responsible_nurse_name?: string | null
  status: string
  extra_info?: PatientExtraInfo | null
  line_user_id?: string | null
  line_reg_code?: string | null
  line_display_name?: string | null
  line_picture_url?: string | null
}

export interface AssessmentResult {
  result_id: number
  assessment_id: number
  overall_risk: string | null
  flow_results: Record<string, FlowResult> | null
  clinical_summary: string | null
  qa_answer: QAAnswer | null
  qa_chunks: { content: string; metadata: Record<string, string> }[] | null
  needs_review: boolean
  reviewed_by: number | null
  created_at: string
}

export interface FlowResult {
  risk_level: string
  recommendation: string | null
  reason: string | null
}

export interface QAAnswer {
  answer: string
  urgency_level: string
  should_contact_doctor: boolean
  related_risks: string[]
}

export interface Assessment {
  assessment_id: number
  patient_hn: string
  created_by: number | null
  submitted_at: string
  symptom_values: Record<string, unknown> | null
  custom_symptoms: unknown[] | null
  additional_questions: string | null
  language: string
  result: AssessmentResult | null
}

export interface DashboardPatient {
  hn: string
  first_name: string
  last_name: string
  phone: string | null
  procedures: string[] | null
  overall_risk: string | null
  last_assessment_at: string | null
  last_assessment_id: number | null
  follow_up_schedules: string[]
  needs_review: boolean
  line_user_id: string | null
  line_reg_code: string | null
  line_display_name?: string | null
  line_picture_url?: string | null
}

export interface DashboardStats {
  total_patients: number
  total_assessments: number
  risk_counts: Record<string, number>
}

export interface Document {
  document_id: number
  filename: string
  file_type: string
  file_size_bytes: number | null
  uploaded_at: string
  uploaded_by: number | null
  rag_status: string
}

export interface RagDocument {
  filename: string       // display name (original, may contain Thai)
  storage_key: string   // ASCII-safe key used for delete/ingest operations
  size: number
  extension: string
  sha256: string | null
  last_ingested: string | null
  is_indexed: boolean
}

export interface IngestStatus {
  status: 'idle' | 'running' | 'done' | 'error'
  mode: string
  message: string
  files_processed: number
  files_total: number
  updated_at: string
  error: string
}

export interface Symptom {
  symptom_id: number
  symptom_name: string
  risk_level: string
  recommendation: string | null
  management_guidance: string | null
  aliases: string[] | null
  managed_by: number | null
}

export type RiskLevel = 'ความเสี่ยงสูง' | 'ความเสี่ยงกลาง' | 'ความเสี่ยงต่ำ' | 'ยังไม่เริ่ม'
