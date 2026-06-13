'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import {
  ChevronLeft, ChevronUp, ChevronDown, Calendar, Pencil, ChevronRight, Link2, Copy, Check, Lock, AlertTriangle, QrCode, X,
  FolderOpen, FileText, User as UserIcon, Phone, MessageCircle, ClipboardList
} from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'
import Navbar from '@/components/layout/Navbar'
import RiskBadge from '@/components/ui/RiskBadge'
import Spinner from '@/components/ui/Spinner'
import ConfirmModal from '@/components/ui/ConfirmModal'
import { useToast } from '@/components/ui/Toast'
import { getAssessment, getPatient, listAssessments, deletePatient, updatePatient, getFormTokens, getMe, updateAssessmentResult } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import type { Assessment, Patient, FlowResult } from '@/lib/types'
import { SYMPTOM_VALUE_EN } from '@/lib/symptom-translations'
import { SYMPTOM_FIELDS, SYMPTOM_SKIP_KEYS, SYMPTOM_LABEL_MAP } from '@/lib/symptom-config'
import { OTHER_SYMPTOMS_MAPPINGS } from '@/lib/symptomMappings'

const FLOW_LABEL_MAP: Record<string, string> = {
  ...SYMPTOM_LABEL_MAP,
  ...Object.fromEntries(OTHER_SYMPTOMS_MAPPINGS.map(m => [m.key, m.labelTH])),
  other_symptoms_custom_flow: 'อาการอื่นๆ (ระบุเพิ่มเติม)',
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmt(iso: string | null | undefined) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('th-TH', { dateStyle: 'short', timeStyle: 'short' })
}


function calcAge(dob: string | null | undefined) {
  if (!dob) return '-'
  return Math.floor((Date.now() - new Date(dob).getTime()) / (365.25 * 24 * 3600 * 1000)) + ' ปี'
}

const RISK_LEFT: Record<string, string> = {
  'ความเสี่ยงสูง': 'border-l-red-500 bg-red-50',
  'ความเสี่ยงกลาง': 'border-l-yellow-400 bg-yellow-50',
  'ความเสี่ยงต่ำ': 'border-l-green-500 bg-green-50',
  'High Risk': 'border-l-red-500 bg-red-50',
  'Medium Risk': 'border-l-yellow-400 bg-yellow-50',
  'Low Risk': 'border-l-green-500 bg-green-50',
}

function formatSymptomValue(val: unknown, lang?: string): string {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'boolean') return val ? (lang === 'en' ? 'Yes' : 'ใช่') : (lang === 'en' ? 'No' : 'ไม่ใช่')
  if (Array.isArray(val)) {
    if (!val.length) return '-'
    return val.map(v => (lang === 'en' ? (SYMPTOM_VALUE_EN[String(v)] ?? String(v)) : String(v))).join(', ')
  }
  const s = String(val)
  return lang === 'en' ? (SYMPTOM_VALUE_EN[s] ?? s) : s
}

// ─── Symptom Data Panel ───────────────────────────────────────────────────────

const FLOW_RISK_COLOR: Record<string, string> = {
  'ความเสี่ยงสูง': '#ef4444',
  'ความเสี่ยงกลาง': '#eab308',
  'ความเสี่ยงต่ำ': '#22c55e',
  'ซับซ้อน': '#f97316',
  'High Risk': '#ef4444',
  'Medium Risk': '#eab308',
  'Low Risk': '#22c55e',
  'Complicated': '#f97316',
}

function FlowSquare({ flowName, flow }: { flowName: string; flow: FlowResult }) {
  const [show, setShow] = useState(false)
  const color = FLOW_RISK_COLOR[flow.risk_level] ?? '#9ca3af'
  return (
    <div className="relative" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      <div className="w-4 h-4 rounded-sm cursor-pointer" style={{ backgroundColor: color }} />
      {show && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 bg-gray-900 text-white text-xs rounded-lg p-3 z-50 shadow-xl pointer-events-none">
          <div className="font-semibold mb-1 text-yellow-300">{FLOW_LABEL_MAP[flowName] ?? flowName}</div>
          <div className="mb-1"><span className="text-gray-400">ระดับ: </span>{flow.risk_level}</div>
          {flow.reason && <div className="mb-1"><span className="text-gray-400">เหตุผล: </span>{flow.reason}</div>}
          {flow.recommendation && <div><span className="text-gray-400">คำแนะนำ: </span>{flow.recommendation}</div>}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </div>
      )}
    </div>
  )
}


function SymptomDataPanel({ assessment, flowResults }: { assessment: Assessment; flowResults: Record<string, FlowResult> | null }) {
  const [open, setOpen] = useState(true)
  const sv = assessment.symptom_values ?? {}
  const knownKeys = new Set(SYMPTOM_FIELDS.map(f => f.key))
  const orderedKeys = SYMPTOM_FIELDS.map(f => f.key).filter(k => k in sv)
  const extraKeys = Object.keys(sv).filter(k => !knownKeys.has(k) && !SYMPTOM_SKIP_KEYS.has(k))
  const entries = [...orderedKeys, ...extraKeys].map(k => [k, sv[k]] as [string, unknown])
  const flows = flowResults ? Object.entries(flowResults) : []
  const lang = assessment.language

  if (entries.length === 0) return null

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
      <div className="flex items-center justify-between px-5 py-3 hover:bg-gray-50 transition-colors rounded-t-xl">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-sm font-semibold text-gray-800"><FolderOpen className="w-4 h-4 text-gray-500" /> ข้อมูลที่กรอกมา</span>
          {flows.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] text-gray-400">ความเสี่ยงรายอาการ:</span>
              <div className="flex gap-0.5">
                {flows.map(([name, flow]) => (
                  <FlowSquare key={name} flowName={name} flow={flow} />
                ))}
              </div>
            </div>
          )}
        </div>
        <button onClick={() => setOpen(o => !o)} className="text-gray-400 hover:text-gray-600">
          {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>
      {open && (
        <div className="px-5 pb-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
            {entries.map(([key, val]) => (
              <div key={key}>
                <div className="text-xs font-medium text-gray-500 mb-0.5">
                  {SYMPTOM_FIELDS.find(f => f.key === key)?.label ?? key.replace(/_/g, ' ')}
                </div>
                <div className="text-sm text-gray-800">{formatSymptomValue(val, lang)}</div>
              </div>
            ))}
            {assessment.custom_symptoms && assessment.custom_symptoms.length > 0 && (
              <div className="col-span-2">
                <div className="text-xs font-medium text-gray-500 mb-0.5">อาการเพิ่มเติม (กรอกเอง)</div>
                <div className="text-sm text-gray-800">
                  {assessment.custom_symptoms.map((c: unknown) => {
                    if (c && typeof c === 'object' && 'symptom' in c) {
                      const o = c as { symptom?: string; detail?: string }
                      return [o.symptom, o.detail].filter(Boolean).join(': ')
                    }
                    return String(c)
                  }).join(', ')}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Summary Panel ───────────────────────────────────────────────────────────

function SummaryPanel({ assessment, onUpdated }: { assessment: Assessment; onUpdated: (a: Assessment) => void }) {
  const result = assessment.result
  const { success, error } = useToast()
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState('')
  const [saving, setSaving] = useState(false)

  if (!result) return null

  const hasCustomSymptoms = (assessment.custom_symptoms?.length ?? 0) > 0
  const needsReview = result.needs_review
  const riskBorder = RISK_LEFT[result.overall_risk ?? ''] || 'border-l-gray-300 bg-gray-50'
  const displayText = result.clinical_summary?.replace(/\\n/g, '\n') ?? ''

  const startEdit = () => { setDraft(displayText); setEditing(true) }
  const cancelEdit = () => setEditing(false)

  const save = async () => {
    setSaving(true)
    try {
      const updated = await updateAssessmentResult(assessment.assessment_id, { clinical_summary: draft })
      onUpdated(updated)
      setEditing(false)
      success('บันทึกสรุปผลเรียบร้อยแล้ว')
    } catch {
      error('บันทึกไม่สำเร็จ กรุณาลองใหม่')
    } finally {
      setSaving(false)
    }
  }

  const markReviewed = async () => {
    setSaving(true)
    try {
      const updated = await updateAssessmentResult(assessment.assessment_id, { needs_review: false, confirm_question: true, confirm_custom: true, confirm_conflict: true })
      onUpdated(updated)
      success('ยืนยันการตรวจสอบเรียบร้อยแล้ว')
    } catch {
      error('เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-gray-800">สรุปผลการประเมินและคำแนะนำจาก AI</h2>
        {!editing && needsReview && (
          <button onClick={startEdit} className="text-xs text-gray-400 hover:text-primary flex items-center gap-1 transition-colors">
            <Pencil className="w-3 h-3" /> แก้ไข
          </button>
        )}
      </div>

      {hasCustomSymptoms && needsReview && (
        <div className="mb-3 flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          <div className="flex-1 text-xs text-amber-800">
            <span className="font-semibold">รอตรวจสอบ</span> — ผู้ป่วยกรอกอาการเพิ่มเติม ควรตรวจสอบสรุปผลก่อนส่งต่อ
          </div>
          <button
            onClick={markReviewed}
            disabled={saving}
            className="text-xs font-medium text-amber-700 hover:text-amber-900 underline shrink-0 disabled:opacity-50"
          >
            ยืนยันแล้ว
          </button>
        </div>
      )}

      {editing ? (
        <div className="space-y-2">
          <textarea
            className="w-full text-sm text-gray-700 leading-relaxed border border-gray-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
            rows={10}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            autoFocus
          />
          <div className="flex gap-2 justify-end">
            <button onClick={cancelEdit} className="btn btn-ghost text-sm px-3 py-1.5">ยกเลิก</button>
            <button onClick={save} disabled={saving} className="btn btn-primary text-sm px-3 py-1.5 disabled:opacity-50">
              {saving ? 'กำลังบันทึก...' : 'บันทึก'}
            </button>
          </div>
        </div>
      ) : (
        <div className={`rounded-lg px-4 py-4 border-l-4 ${riskBorder}`}>
          {displayText
            ? <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{displayText}</p>
            : <p className="text-sm text-gray-400">ไม่มีสรุปผล</p>}
        </div>
      )}
    </div>
  )
}

// ─── QA Panel ────────────────────────────────────────────────────────────────

function QAPanel({ assessment, onUpdated }: { assessment: Assessment; onUpdated: (a: Assessment) => void }) {
  const result = assessment.result
  const { success, error } = useToast()
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState('')
  const [saving, setSaving] = useState(false)
  const [showChunks, setShowChunks] = useState(false)

  if (!result?.qa_answer || !assessment.additional_questions) return null

  const chunks = result.qa_chunks ?? []

  const needsReview = result.needs_review
  const displayAnswer = result.qa_answer.answer ?? ''

  const startEdit = () => { setDraft(displayAnswer); setEditing(true) }
  const cancelEdit = () => setEditing(false)

  const save = async (markDone: boolean) => {
    setSaving(true)
    try {
      const updated = await updateAssessmentResult(assessment.assessment_id, {
        qa_answer_text: draft,
        ...(markDone ? { needs_review: false } : {}),
      })
      onUpdated(updated)
      setEditing(false)
      success(markDone ? 'บันทึกและยืนยันเรียบร้อยแล้ว' : 'บันทึกคำตอบเรียบร้อยแล้ว')
    } catch {
      error('บันทึกไม่สำเร็จ กรุณาลองใหม่')
    } finally {
      setSaving(false)
    }
  }

  const markReviewed = async () => {
    setSaving(true)
    try {
      const updated = await updateAssessmentResult(assessment.assessment_id, { needs_review: false, confirm_question: true, confirm_custom: true, confirm_conflict: true })
      onUpdated(updated)
      success('ยืนยันการตรวจสอบเรียบร้อยแล้ว')
    } catch {
      error('เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-gray-800">คำถามเพิ่มเติมจากผู้ป่วย</h2>
        {!editing && (
          <button onClick={startEdit} className="text-xs text-gray-400 hover:text-primary flex items-center gap-1 transition-colors">
            <Pencil className="w-3 h-3" /> แก้ไข
          </button>
        )}
      </div>

      {needsReview && !editing && (
        <div className="mb-3 flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          <div className="flex-1 text-xs text-amber-800">
            <span className="font-semibold">รอตรวจสอบ</span> — ผู้ป่วยมีคำถาม ตรวจสอบคำตอบของ AI ก่อนส่งต่อ
          </div>
          <button
            onClick={markReviewed}
            disabled={saving}
            className="text-xs font-medium text-amber-700 hover:text-amber-900 underline shrink-0 disabled:opacity-50"
          >
            ยืนยันแล้ว
          </button>
        </div>
      )}

      <div className="text-sm text-gray-600 mb-3 bg-gray-50 rounded-lg px-3 py-2">
        <span className="font-medium text-gray-500 text-xs">คำถาม: </span>{assessment.additional_questions}
      </div>

      {editing ? (
        <div className="space-y-2">
          <textarea
            className="w-full text-sm text-gray-700 leading-relaxed border border-gray-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
            rows={5}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            autoFocus
          />
          <div className="flex gap-2 justify-end">
            <button onClick={cancelEdit} disabled={saving} className="btn btn-ghost text-sm px-3 py-1.5">ยกเลิก</button>
            <button onClick={() => save(false)} disabled={saving} className="text-sm px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-700 disabled:opacity-50">
              {saving ? '...' : 'บันทึก'}
            </button>
            <button onClick={() => save(true)} disabled={saving} className="btn btn-primary text-sm px-3 py-1.5 disabled:opacity-50">
              {saving ? 'กำลังบันทึก...' : 'บันทึกและยืนยัน'}
            </button>
          </div>
        </div>
      ) : (
        <div className="text-sm text-gray-700 leading-relaxed bg-gray-50 rounded-lg px-4 py-3 whitespace-pre-line">
          {displayAnswer || <span className="text-gray-400">ไม่มีคำตอบ</span>}
        </div>
      )}

      {!editing && (
        <>
          <div className="flex items-center justify-between flex-wrap gap-2 mt-3">
            <div className="flex gap-2 flex-wrap">

              {result.qa_answer.should_contact_doctor && (
                <span className="text-xs bg-red-50 text-red-600 px-2 py-1 rounded-full">ควรติดต่อแพทย์</span>
              )}
            </div>
            {chunks.length > 0 && (
              <button
                onClick={() => setShowChunks(v => !v)}
                className="text-xs text-gray-400 hover:text-primary flex items-center gap-1 transition-colors"
              >
                <ChevronDown className={`w-3 h-3 transition-transform ${showChunks ? 'rotate-180' : ''}`} />
                แหล่งข้อมูล ({chunks.length})
              </button>
            )}
          </div>

          {showChunks && chunks.length > 0 && (
            <div className="mt-3 space-y-2">
              <div className="text-xs font-medium text-gray-500 mb-1">เอกสารที่ AI ใช้ตอบคำถาม</div>
              {chunks.map((chunk, i) => (
                <div key={i} className="border border-gray-100 rounded-lg p-3 bg-gray-50">
                  {chunk.metadata?.source && (
                    <div className="text-xs text-primary font-medium mb-1 truncate">
                      <FileText className="w-3 h-3 inline shrink-0 mr-1" />{chunk.metadata.source}
                    </div>
                  )}
                  <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-line">
                    {chunk.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ─── Form Link Banner ─────────────────────────────────────────────────────────

function findLink(
  links: Record<string, { url: string; password: string; token?: string }>,
  dateStr: string
) {
  if (links[dateStr]) return links[dateStr]
  try {
    const target = new Date(dateStr).getTime()
    for (const [key, val] of Object.entries(links)) {
      if (Math.abs(new Date(key).getTime() - target) < 60_000) return val
    }
  } catch {}
  return undefined
}

function FormLinkBanner({
  linkKey,
  link,
  copiedKey,
  onCopy,
}: {
  linkKey: string
  link: { url: string; password: string; token?: string }
  copiedKey: string | null
  onCopy: (key: string, text: string) => void
}) {
  return (
    <div className="mt-3 bg-slate-50 rounded-xl border border-slate-200 p-3 flex flex-col gap-2">
      {/* URL row */}
      <div className="flex items-center gap-2 min-w-0">
        <div className="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <Link2 className="w-3.5 h-3.5" />
        </div>
        <a
          href={link.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-gray-500 hover:text-primary hover:underline truncate flex-1 min-w-0"
          title={link.url}
        >
          {link.url}
        </a>
        <button
          onClick={() => onCopy(`${linkKey}-url`, link.url)}
          title="คัดลอกลิงก์"
          className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 bg-white hover:border-primary/40 hover:bg-primary/5 text-gray-400 hover:text-primary transition-all"
        >
          {copiedKey === `${linkKey}-url` ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Password row */}
      <div className="flex items-center gap-2 bg-white rounded-lg border border-slate-200 px-3 py-2 min-w-0">
        <Lock className="w-3.5 h-3.5 text-gray-400 shrink-0" />
        <span className="text-xs text-gray-400 shrink-0">รหัสผ่าน</span>
        <span className="font-mono font-bold text-gray-800 text-sm tracking-widest flex-1">{link.password}</span>
        <button
          onClick={() => onCopy(`${linkKey}-pw`, link.password)}
          title="คัดลอกรหัสผ่าน"
          className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 bg-slate-50 hover:border-primary/40 hover:bg-primary/5 text-gray-400 hover:text-primary transition-all"
        >
          {copiedKey === `${linkKey}-pw` ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
      </div>
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function PatientDetailPage() {
  const router = useRouter()
  const { hn } = useParams<{ hn: string }>()
  const searchParams = useSearchParams()
  const assessmentIdParam = searchParams.get('assessment')
  const { success, error } = useToast()

  const [patient, setPatient] = useState<Patient | null>(null)
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [selected, setSelected] = useState<Assessment | null>(null)
  const [loading, setLoading] = useState(true)
  // key = scheduleDate string (or 'general' for no-schedule link)
  const [generatedLinks, setGeneratedLinks] = useState<Record<string, { url: string; password: string; token?: string }>>({})
  const [copiedKey, setCopiedKey] = useState<string | null>(null)
  const [showQR, setShowQR] = useState(false)
  const [confirmModal, setConfirmModal] = useState<{ type: 'cancel' | 'close' } | null>(null)

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    getMe().then(u => {
      if (!u.roles?.includes('view_cases') && !u.roles?.includes('view_all_cases')) { router.push('/login'); return }
      load()
    }).catch(() => router.push('/login'))
  }, [hn])

  const load = async () => {
    setLoading(true)
    try {
      const [p, list] = await Promise.all([
        getPatient(hn),
        listAssessments({ patient_hn: hn, limit: 20 }),
      ])
      setPatient(p)
      setAssessments(list)
      const targetId = assessmentIdParam ? parseInt(assessmentIdParam) : list[0]?.assessment_id
      if (targetId) setSelected(await getAssessment(targetId))
      // fetch separately — only available with send_assessment permission
      getFormTokens(hn).then(setGeneratedLinks).catch(() => { })
    } catch (error: any) {
      if (error?.response?.status === 404) {
        router.push('/')
      } else {
        console.error('Failed to load patient data:', error)
      }
    } finally { setLoading(false) }
  }

  // Start a new assessment for this patient
  const openNewAssessment = (scheduleDate?: string) => {
    let url = `/assessments/new?hn=${hn}`
    if (scheduleDate) {
      url += `&schedule=${encodeURIComponent(scheduleDate)}`
    }
    window.open(url, '_blank')
  }

  const handleCancelCase = async () => {
    setConfirmModal(null)
    try {
      await deletePatient(hn)
      success('ลบเคสเรียบร้อยแล้ว')
      router.push('/')
    } catch {
      error('ลบเคสไม่สำเร็จ กรุณาลองใหม่')
    }
  }

  const handleCloseCase = async () => {
    setConfirmModal(null)
    try {
      await updatePatient(hn, { status: 'history' })
      success('ปิดเคสเรียบร้อยแล้ว')
      router.push('/')
    } catch {
      error('ปิดเคสไม่สำเร็จ กรุณาลองใหม่')
    }
  }

  const handleCopy = async (key: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedKey(key)
      setTimeout(() => setCopiedKey(null), 2000)
    } catch {
      error('คัดลอกไม่สำเร็จ')
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-50"><Navbar /><div className="flex justify-center py-20"><Spinner className="w-10 h-10" /></div></div>
  )
  if (!patient) return (
    <div className="min-h-screen bg-gray-50"><Navbar /><div className="text-center py-20 text-gray-400">ไม่พบผู้ป่วย</div></div>
  )

  const result = selected?.result

  // The badge at the top should always reflect the latest assessment's risk
  const latestRisk = assessments[0]?.result?.overall_risk

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      {/* QR Modal */}
      {showQR && patient.line_reg_code && (() => {
        const lineOaId = process.env.NEXT_PUBLIC_LINE_OA_ID ?? ''
        const deepLink = `https://line.me/R/ti/p/${lineOaId}`
        return (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={() => setShowQR(false)}>
            <div className="bg-white rounded-2xl shadow-xl p-6 w-[90vw] max-w-xs flex flex-col items-center gap-4" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between w-full">
                <h3 className="font-bold text-gray-800">ลงทะเบียน LINE OA</h3>
                <button onClick={() => setShowQR(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
              </div>
              <p className="text-sm text-gray-500 text-center">
                {patient.first_name} {patient.last_name}<br />
                <span className="text-green-600 font-medium">สแกน QR → LINE เปิด → ส่งรหัสอัตโนมัติ</span>
              </p>
              <QRCodeSVG value={deepLink} size={200} />
              <div className="flex items-center gap-3 bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-2.5 w-full justify-between">
                <div>
                  <div className="text-xs text-yellow-600 mb-0.5">หรือพิมพ์รหัสเอง</div>
                  <span className="font-mono font-bold text-yellow-800 text-xl tracking-widest">{patient.line_reg_code}</span>
                </div>
                <button onClick={() => handleCopy('line-reg-qr', patient.line_reg_code!)} className="text-yellow-600 hover:text-yellow-800">
                  {copiedKey === 'line-reg-qr' ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
                </button>
              </div>
            </div>
          </div>
        )
      })()}

      <main className="max-w-screen-xl mx-auto px-4 py-6 space-y-5">

        {/* Back */}
        <button onClick={() => router.push('/dashboard')} className="flex items-center gap-1 text-sm text-gray-500 hover:text-primary transition-colors">
          <ChevronLeft className="w-4 h-4" /> กลับ
        </button>

        {/* ── Patient Card ── */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">

          {/* Top: identity + actions */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4 flex-1 min-w-0">
              <div className="w-14 h-14 rounded-full bg-purple-100 flex items-center justify-center shrink-0 overflow-hidden">
                {patient.line_picture_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={patient.line_picture_url} alt="LINE profile" className="w-full h-full object-cover" />
                ) : (
                  <UserIcon className="w-7 h-7 text-purple-400" />
                )}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">{patient.first_name} {patient.last_name}</h1>
                  {latestRisk && <RiskBadge risk={latestRisk} size="md" />}
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-0.5 mt-1 text-sm">
                  <span className="font-bold text-gray-800 tracking-wide">HN: {patient.hn}</span>
                  {patient.gender && <span className="text-gray-500">{patient.gender}</span>}
                  {patient.date_of_birth && <span className="text-gray-500">เกิด {patient.date_of_birth} ({calcAge(patient.date_of_birth)})</span>}
                  {patient.phone && <span className="flex items-center gap-1 text-gray-500"><Phone className="w-3.5 h-3.5 shrink-0" />{patient.phone}</span>}
                  {patient.line_display_name && <span className="text-gray-500">LINE: {patient.line_display_name}</span>}
                </div>
                {/* LINE registration status */}
                <div className="mt-2 flex items-center gap-2">
                  {patient.line_user_id ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-green-50 border border-green-200 text-green-700 text-xs font-semibold">
                      <MessageCircle className="w-3.5 h-3.5 shrink-0" /> เชื่อม LINE แล้ว
                    </span>
                  ) : patient.line_reg_code ? (
                    <span className="inline-flex items-center gap-2 px-2.5 py-1 rounded-lg bg-yellow-50 border border-yellow-300 text-yellow-800 text-xs font-semibold">
                      <MessageCircle className="w-3.5 h-3.5 shrink-0" /> รหัสลงทะเบียน LINE:
                      <span className="font-mono tracking-widest">{patient.line_reg_code}</span>
                      <button onClick={() => handleCopy('line-reg', patient.line_reg_code!)} className="text-yellow-600 hover:text-yellow-800">
                        {copiedKey === 'line-reg' ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
                      </button>
                      <button onClick={() => setShowQR(true)} className="text-yellow-600 hover:text-yellow-800" title="แสดง QR Code">
                        <QrCode className="w-3.5 h-3.5" />
                      </button>
                    </span>
                  ) : null}
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1.5 shrink-0">
              <button
                onClick={() => router.push(`/patients/${hn}/edit`)}
                disabled={Boolean(patient.line_user_id)}
                className="btn-outline flex items-center gap-1.5 bg-white text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Pencil className="w-4 h-4" /> แก้ไขข้อมูล
              </button>
              {patient.line_user_id && (
                <span className="flex items-center gap-1 text-[11px] text-gray-400">
                  <Lock className="w-3 h-3" /> ล็อคหลังเชื่อม LINE แล้ว
                </span>
              )}
            </div>
          </div>

          {/* Divider */}
          <div className="mt-5 pt-4 border-t border-gray-100">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-x-6 gap-y-4 text-sm">

              {/* Surgery info */}
              <div>
                <div className="text-xs text-gray-400 mb-1">วันที่ผ่าตัด</div>
                <div className="font-medium text-gray-800">{patient.extra_info?.surgery_date || <span className="text-gray-400 font-normal">-</span>}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">วันที่จำหน่าย</div>
                <div className="font-medium text-gray-800">{patient.extra_info?.discharge_date || <span className="text-gray-400 font-normal">-</span>}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">ประเมินล่าสุด</div>
                <div className="font-medium text-gray-800">{assessments[0] ? fmt(assessments[0].submitted_at) : <span className="text-gray-400 font-normal">-</span>}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">ผู้รับผิดชอบ</div>
                <div className="font-medium text-gray-800">{patient.responsible_nurse_name || patient.responsible_person || <span className="text-gray-400 font-normal">-</span>}</div>
              </div>

              {/* Procedures + Special — full width, merged */}
              <div className="col-span-2 sm:col-span-3 lg:col-span-6">
                <div className="text-xs text-gray-400 mb-2">หัตถการที่ทำ</div>
                {patient.procedures && patient.procedures.length > 0 ? (
                  <div className="space-y-1.5">
                    {/* Procedures with sub-options or tooth numbers get a card */}
                    {(() => {
                      const withMeta: React.ReactNode[] = []
                      const simple: string[] = []

                      patient.procedures!.forEach((p, i) => {
                        const isLefort = p.includes('Lefort I')
                        const isBSSRO = p.includes('BSSRO')
                        const isBiopsy = p.includes('Biopsy')
                        const isSurgical = p.includes('ผ่าตัดถอนฟัน')
                        const isExtraction = p.includes('ถอนฟัน') && !isSurgical
                        const subs = isLefort ? patient.extra_info?.lefort_sub_options
                          : isBSSRO ? patient.extra_info?.bssro_sub_options
                            : isBiopsy ? patient.extra_info?.biopsy_sub_options
                              : null
                        const tooth = isSurgical ? patient.extra_info?.surgical_tooth_numbers
                          : isExtraction ? patient.extra_info?.extraction_tooth_numbers
                            : null
                        const hasMeta = (subs && subs.length > 0) || tooth

                        if (hasMeta) {
                          withMeta.push(
                            <div key={i} className="flex flex-col gap-1.5 px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                              <span className="text-sm font-medium text-gray-800">• {p}</span>
                              {subs && subs.length > 0 && (
                                <div className="flex flex-wrap gap-1 pl-3">
                                  {subs.map(s => (
                                    <span key={s} className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-100 text-blue-700 border border-blue-200">{s}</span>
                                  ))}
                                </div>
                              )}
                              {tooth && (
                                <span className="pl-3 text-xs text-gray-500">ฟันซี่: <span className="font-medium text-gray-700">{tooth}</span></span>
                              )}
                            </div>
                          )
                        } else {
                          simple.push(p)
                        }
                      })

                      return (
                        <>
                          {withMeta}
                          {simple.length > 0 && (
                            <div className="flex flex-wrap gap-1.5 pt-0.5">
                              {simple.map((p, i) => (
                                <span key={i} className="inline-flex items-center px-2.5 py-1 rounded-md text-xs text-gray-700 bg-gray-100 border border-gray-200">
                                  {p}
                                </span>
                              ))}
                            </div>
                          )}
                        </>
                      )
                    })()}

                    {/* Special devices — uniform color, clearly static (no hover) */}
                    {(patient.extra_info?.imf_wire || patient.extra_info?.imf_elastic || patient.extra_info?.special_icbg || patient.extra_info?.special_ng_tube) && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-gray-100">
                        <span className="text-xs text-gray-400 mr-1">หัตถการเสริมที่ทำ:</span>
                        {patient.extra_info?.imf_wire && (
                          <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 select-none">
                            IMF ลวด{patient.extra_info.imf_wire_loops ? ` · ${patient.extra_info.imf_wire_loops} loops` : ''}
                          </span>
                        )}
                        {patient.extra_info?.imf_elastic && (
                          <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 select-none">
                            IMF ยาง{patient.extra_info.imf_elastic_loops ? ` · ${patient.extra_info.imf_elastic_loops} loops` : ''}
                          </span>
                        )}
                        {patient.extra_info?.special_icbg && (
                          <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 select-none">
                            ICBG{patient.extra_info.special_icbg_description ? ` · ${patient.extra_info.special_icbg_description}` : ''}
                          </span>
                        )}
                        {patient.extra_info?.special_ng_tube && (
                          <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 select-none">
                            NG Tube{patient.extra_info.special_ng_tube_description ? ` · ${patient.extra_info.special_ng_tube_description}` : ''}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ) : <span className="text-gray-400 text-sm">-</span>}

                  {/* Note — shown below หัตถการเสริม */}
                  {patient.extra_info?.note && (
                    <div className="flex items-start gap-1.5 text-xs text-gray-600 pt-2 border-t border-gray-100 mt-1">
                      <span className="text-gray-400 font-medium shrink-0">โน็ต:</span>
                      <span>{patient.extra_info.note}</span>
                    </div>
                  )}
              </div>
            </div>
          </div>
        </div>

        {/* ── Main content: Timeline + Right panel ── */}
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-5">

          {/* LEFT: Timeline */}
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
              <h2 className="font-semibold text-gray-800 mb-3 text-sm">ประวัติการประเมิน</h2>
              {assessments.length === 0
                ? <p className="text-sm text-gray-400">ยังไม่มีการประเมิน</p>
                : (
                  <div className="space-y-2">
                    {assessments.map(a => {
                      const ar = a as Assessment & { overall_risk?: string }
                      const isActive = selected?.assessment_id === a.assessment_id
                      const riskKey = ar.overall_risk ?? ''
                      return (
                        <button key={a.assessment_id} onClick={async () => setSelected(await getAssessment(a.assessment_id))}
                          className={`w-full text-left px-3 py-2.5 rounded-lg border-l-4 transition-colors ${isActive
                            ? (RISK_LEFT[riskKey] || 'border-l-primary bg-primary/5')
                            : 'border-l-gray-200 bg-gray-50 hover:bg-gray-100'}`}>
                          <div className="text-xs font-semibold text-gray-700">
                            {new Date(a.submitted_at).toLocaleDateString('th-TH', { day: '2-digit', month: 'long', year: 'numeric' })}
                          </div>
                          <div className="text-[11px] text-gray-400 mt-0.5">บันทึกเวลา {new Date(a.submitted_at).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })} น.</div>
                          {ar.overall_risk && <div className="mt-1"><RiskBadge risk={ar.overall_risk} /></div>}
                        </button>
                      )
                    })}
                  </div>
                )
              }
            </div>

            {/* Upcoming Schedule (Only show if active) */}
            {patient?.status === 'active' && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mt-6">
                <h2 className="text-base font-bold text-gray-900 mb-4">กำหนดการติดตาม</h2>
                {patient?.follow_up_schedules?.length ? (
                  <div className="space-y-3">
                    {patient.follow_up_schedules.map((dateStr, idx) => (
                      <div key={idx} className="rounded-lg border border-gray-100 p-2 overflow-hidden">
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-start gap-2 text-sm">
                            <Calendar className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                            <div>
                              <div className="font-medium text-gray-700">นัดติดตามครั้งที่ {idx + 1}</div>
                              <div className="text-gray-500 text-xs mt-0.5">
                                {new Date(dateStr).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' })}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1.5 shrink-0">
                            <button
                              onClick={() => openNewAssessment(dateStr)}
                              className="text-[11px] text-gray-500 border border-gray-200 px-2 py-1 rounded-lg hover:bg-gray-50 flex items-center gap-1"
                            >
                              ประเมิน <ChevronRight className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                        {(() => { const link = findLink(generatedLinks, dateStr); return link ? <FormLinkBanner linkKey={dateStr} link={link} copiedKey={copiedKey} onCopy={handleCopy} /> : null })()}
                      </div>
                    ))}
                  </div>
                ) : patient?.follow_up_date ? (
                  <div className="rounded-lg border border-gray-100 p-2 overflow-hidden">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-start gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <div>
                          <div className="font-medium text-gray-700">นัดติดตาม</div>
                          <div className="text-gray-500 text-xs mt-0.5">
                            {new Date(patient.follow_up_date).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' })}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        <button
                          onClick={() => openNewAssessment(patient.follow_up_date ?? undefined)}
                          className="text-[11px] text-gray-500 border border-gray-200 px-2 py-1 rounded-lg hover:bg-gray-50 flex items-center gap-1"
                        >
                          ประเมิน <ChevronRight className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                    {(() => { const link = findLink(generatedLinks, patient.follow_up_date ?? ''); return link ? <FormLinkBanner linkKey={patient.follow_up_date!} link={link} copiedKey={copiedKey} onCopy={handleCopy} /> : null })()}
                  </div>
                ) : (
                  <div className="flex items-start gap-2 text-sm">
                    <Calendar className="w-4 h-4 text-gray-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-400">ยังไม่มีกำหนดการ</div>
                      <div className="text-gray-400 text-xs mt-0.5">
                        กำหนดจากฟอร์มสร้างผู้ป่วย
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}


          </div>

          {/* RIGHT: AI summary + Q&A + Symptom data */}
          <div className="space-y-4">
            {selected && result ? (
              <>
                {/* AI Summary */}
                <SummaryPanel
                  assessment={selected}
                  onUpdated={(updated) => setSelected(updated)}
                />

                {/* Q&A */}
                <QAPanel
                  assessment={selected}
                  onUpdated={(updated) => setSelected(updated)}
                />

                {/* Symptom data */}
                <SymptomDataPanel assessment={selected} flowResults={result?.flow_results ?? null} />

                {/* Bottom actions */}
                <div className="flex justify-end gap-3 pt-2">
                  {patient.status === 'history' ? (
                    <button onClick={() => setConfirmModal({ type: 'cancel' })} className="btn-outline text-red-500 border-red-300 hover:bg-red-50 hover:text-red-600 hover:border-red-400">
                      ลบเคส
                    </button>
                  ) : (
                    <>
                      <button onClick={() => setConfirmModal({ type: 'cancel' })} className="btn-outline text-red-500 border-red-300 hover:bg-red-50 hover:text-red-600 hover:border-red-400">
                        ยกเลิกเคส
                      </button>
                      <button onClick={() => setConfirmModal({ type: 'close' })} className="btn-primary bg-gray-700 hover:bg-gray-800">
                        ปิดเคส
                      </button>
                    </>
                  )}
                </div>
              </>
            ) : (
              <div className="space-y-4">
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm flex flex-col items-center justify-center py-20 text-gray-400 gap-3">
                  <ClipboardList className="w-10 h-10 text-gray-300" />
                  <p className="text-sm">ยังไม่มีการประเมิน</p>
                </div>
                {/* Bottom actions */}
                <div className="flex justify-end gap-3 pt-2">
                  {patient.status === 'history' ? (
                    <button onClick={() => setConfirmModal({ type: 'cancel' })} className="btn-outline text-red-500 border-red-300 hover:bg-red-50 hover:text-red-600 hover:border-red-400">
                      ลบเคส
                    </button>
                  ) : (
                    <button onClick={() => setConfirmModal({ type: 'cancel' })} className="btn-outline text-red-500 border-red-300 hover:bg-red-50 hover:text-red-600 hover:border-red-400">
                      ยกเลิกเคส
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <ConfirmModal
        open={confirmModal?.type === 'cancel'}
        title={patient.status === 'history' ? 'ลบเคส' : 'ยกเลิกเคส'}
        message={patient.status === 'history' ? 'เคสนี้จะถูกลบถาวร ไม่สามารถกู้คืนได้' : 'เคสจะถูกลบออกจากระบบ ต้องการดำเนินการต่อหรือไม่?'}
        confirmLabel={patient.status === 'history' ? 'ลบเคส' : 'ยกเลิกเคส'}
        danger
        onConfirm={handleCancelCase}
        onCancel={() => setConfirmModal(null)}
      />
      <ConfirmModal
        open={confirmModal?.type === 'close'}
        title="ปิดเคส"
        message="เคสจะถูกย้ายไปยังประวัติ ยังสามารถดูข้อมูลย้อนหลังได้"
        confirmLabel="ปิดเคส"
        onConfirm={handleCloseCase}
        onCancel={() => setConfirmModal(null)}
      />
    </div>
  )
}
