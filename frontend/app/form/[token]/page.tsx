'use client'

import { Suspense, useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { ArrowLeft, ArrowRight, CheckCircle, Loader2, AlertCircle, Lock, User, Phone, Calendar, Stethoscope } from 'lucide-react'
import type { PatientFormData } from '@/lib'
import { th, en } from '@/lib/locales'
import SymptomsForm from '@/components/forms/SymptomsForm'
import DailyLifeForm from '@/components/forms/DailyLifeForm'
import { checkFormToken, unlockPublicForm, submitPublicForm } from '@/lib/api'

const UI = {
  th: {
    formTitle: 'แบบประเมินอาการหลังผ่าตัดทันตกรรม',
    patient: 'ผู้ป่วย:',
    schedule: 'กำหนดการ:',
    lockTitle: 'แบบประเมินอาการหลังผ่าตัด',
    lockSubtitle: 'กรอกรหัสที่ได้รับจากเจ้าหน้าที่เพื่อเข้าถึงแบบประเมิน',
    unlockBtn: 'ปลดล็อกแบบประเมิน',
    unlocking: 'กำลังตรวจสอบ...',
    errorTitle: 'ไม่สามารถเข้าถึงแบบประเมินได้',
    successTitle: 'ส่งแบบประเมินสำเร็จ',
    successMsg: 'บันทึกข้อมูลของคุณเรียบร้อยแล้ว',
    successLine: 'ผลการประเมินและคำแนะนำเพิ่มเติมจะถูกส่งแจ้งเตือนผ่านช่องทาง LINE OA อีกครั้ง',
    prev: 'ย้อนกลับ',
    next: 'ถัดไป',
    submit: 'ส่งและประเมิน',
    submitting: 'กำลังส่งข้อมูล...',
    langToggle: 'EN',
  },
  en: {
    formTitle: 'Post-Operative Dental Assessment',
    patient: 'Patient:',
    schedule: 'Appointment:',
    lockTitle: 'Post-Operative Symptom Assessment',
    lockSubtitle: 'Enter the code provided by your healthcare staff to access the assessment form',
    unlockBtn: 'Unlock Assessment',
    unlocking: 'Verifying...',
    errorTitle: 'Unable to Access Assessment',
    successTitle: 'Assessment Submitted Successfully',
    successMsg: 'Your information has been recorded.',
    successLine: 'Results and additional recommendations will be sent via LINE OA.',
    prev: 'Back',
    next: 'Next',
    submit: 'Submit & Assess',
    submitting: 'Submitting...',
    langToggle: 'ภาษาไทย',
  },
}

function PatientConfirmStep({ data, lang, onReady }: {
  data: PatientFormData
  lang: 'th' | 'en'
  onReady: (valid: boolean) => void
}) {
  useEffect(() => { onReady(true) }, [onReady])

  const labels = lang === 'th'
    ? { title: 'ตรวจสอบข้อมูลของคุณ', subtitle: 'กรุณาตรวจสอบข้อมูลด้านล่างก่อนเริ่มกรอกแบบประเมิน', name: 'ชื่อ-นามสกุล', phone: 'เบอร์โทรศัพท์', dob: 'วันเกิด', gender: 'เพศ', surgeryDate: 'วันที่ผ่าตัด', dischargeDate: 'วันที่จำหน่าย', procedures: 'หัตถการที่รับการรักษา', note: 'หมายเหตุ', infoCorrect: 'หากข้อมูลไม่ถูกต้อง กรุณาติดต่อเจ้าหน้าที่' }
    : { title: 'Confirm Your Information', subtitle: 'Please verify your details below before starting the assessment', name: 'Full Name', phone: 'Phone', dob: 'Date of Birth', gender: 'Gender', surgeryDate: 'Surgery Date', dischargeDate: 'Discharge Date', procedures: 'Procedures', note: 'Note', infoCorrect: 'If any information is incorrect, please contact the staff.' }

  const formatDate = (d?: string) => {
    if (!d) return null
    return new Date(d).toLocaleDateString(lang === 'th' ? 'th-TH' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
  }

  const rows = [
    { icon: <User className="w-4 h-4" />, label: labels.name, value: [data.first_name, data.last_name].filter(Boolean).join(' ') || '-' },
    { icon: <Phone className="w-4 h-4" />, label: labels.phone, value: data.phone || '-' },
    { icon: <Calendar className="w-4 h-4" />, label: labels.dob, value: formatDate(data.birth_date) || '-' },
    { icon: <User className="w-4 h-4" />, label: labels.gender, value: data.gender || '-' },
    ...(data.surgery_date ? [{ icon: <Calendar className="w-4 h-4" />, label: labels.surgeryDate, value: formatDate(data.surgery_date) || data.surgery_date }] : []),
    ...(data.discharge_date ? [{ icon: <Calendar className="w-4 h-4" />, label: labels.dischargeDate, value: formatDate(data.discharge_date) || data.discharge_date }] : []),
  ]

  return (
    <div>
      <div className="flex items-center gap-2 mb-1">
        <CheckCircle className="w-5 h-5 text-primary" />
        <h2 className="font-semibold text-gray-900 text-base">{labels.title}</h2>
      </div>
      <p className="text-sm text-gray-500 mb-5">{labels.subtitle}</p>

      <div className="space-y-3 mb-5">
        {rows.map(row => (
          <div key={row.label} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-400 mt-0.5 shrink-0">{row.icon}</span>
            <div className="min-w-0">
              <div className="text-xs text-gray-400 mb-0.5">{row.label}</div>
              <div className="text-sm font-medium text-gray-800 break-words">{row.value}</div>
            </div>
          </div>
        ))}

        {(data.procedures?.length ?? 0) > 0 && (
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-400 mt-0.5 shrink-0"><Stethoscope className="w-4 h-4" /></span>
            <div className="min-w-0">
              <div className="text-xs text-gray-400 mb-1">{labels.procedures}</div>
              <div className="flex flex-wrap gap-1.5">
                {data.procedures!.map(p => (
                  <span key={p} className="inline-block text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">{p}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {data.note && (
          <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-100">
            <span className="text-amber-400 mt-0.5 shrink-0"><Stethoscope className="w-4 h-4" /></span>
            <div className="min-w-0">
              <div className="text-xs text-amber-500 mb-0.5">{labels.note}</div>
              <div className="text-sm text-amber-800 break-words">{data.note}</div>
            </div>
          </div>
        )}
      </div>

      <p className="text-xs text-gray-400 text-center">{labels.infoCorrect}</p>
    </div>
  )
}

function PublicFormContent() {
  const { token } = useParams<{ token: string }>()
  const [lang, setLang] = useState<'th' | 'en'>('th')

  const ui = UI[lang]
  const t = lang === 'th' ? th.form : en.form
  const STEPS = [
    { id: 1, title: t.steps.basicInfo, description: t.steps.description[1] },
    { id: 2, title: t.steps.symptoms, description: t.steps.description[2] },
    { id: 3, title: t.steps.dailyLife, description: t.steps.description[3] },
  ]

  // Gate state
  const [tokenError, setTokenError] = useState<string | null>(null)
  const [tokenLoading, setTokenLoading] = useState(true)
  const [password, setPassword] = useState('')
  const [unlocking, setUnlocking] = useState(false)
  const [unlockError, setUnlockError] = useState<string | null>(null)
  const [unlocked, setUnlocked] = useState(false)

  // Form state
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<PatientFormData>({})
  const [isCurrentStepValid, setIsCurrentStepValid] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [patientName, setPatientName] = useState('')
  const [scheduleDate, setScheduleDate] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    checkFormToken(token)
      .catch((err) => {
        const s = err?.response?.status
        if (s === 410) setTokenError('ลิงก์นี้หมดอายุแล้ว กรุณาติดต่อเจ้าหน้าที่เพื่อขอลิงก์ใหม่')
        else setTokenError('ลิงก์ไม่ถูกต้อง กรุณาตรวจสอบ URL อีกครั้ง')
      })
      .finally(() => setTokenLoading(false))
  }, [token])

  const handleUnlock = async () => {
    if (!password.trim()) return
    setUnlocking(true)
    setUnlockError(null)
    try {
      const info = await unlockPublicForm(token, password)
      setPatientName(`${info.first_name} ${info.last_name}`)
      setScheduleDate(info.schedule_date ?? null)
      setFormData({
        first_name: info.first_name,
        last_name: info.last_name,
        phone: info.phone ?? undefined,
        gender: info.gender ?? undefined,
        birth_date: info.date_of_birth ?? undefined,
        procedures: info.procedures ?? undefined,
        surgery_date: info.surgery_date ?? undefined,
        discharge_date: info.discharge_date ?? undefined,
        note: info.note ?? undefined,
      })
      setUnlocked(true)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setUnlockError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setUnlocking(false)
    }
  }

  const handleFormDataChange = (data: Partial<PatientFormData>) =>
    setFormData(prev => ({ ...prev, ...data }))

  const handleNext = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(s => s + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(s => s - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    setSubmitError(null)
    try {
      await submitPublicForm(token, {
        password,
        basic_info: {
          first_name: formData.first_name,
          last_name: formData.last_name,
          gender: formData.gender,
          birth_date: formData.birth_date,
          phone: formData.phone,
          procedures: formData.procedures ?? [],
          surgery_date: formData.surgery_date,
          discharge_date: formData.discharge_date,
          note: formData.note,
          imf_wire: formData.imf_wire,
          imf_wire_loops: formData.imf_wire_loops,
          imf_elastic: formData.imf_elastic,
          imf_elastic_loops: formData.imf_elastic_loops,
          special_icbg: formData.special_icbg,
          special_ng_tube: formData.special_ng_tube,
          lefort_sub_options: formData.lefort_sub_options,
          bssro_sub_options: formData.bssro_sub_options,
        },
        symptom_values: {
          pain_score: formData.pain_score,
          pain_description: formData.pain_description,
          pain_medication_effect: formData.pain_medication_effect,
          swelling_status: formData.swelling_status,
          breathing_or_swallowing_difficulty: formData.breathing_or_swallowing_difficulty,
          bleeding_status: formData.bleeding_status,
          fever_status: formData.fever_status,
          numbness_status: formData.numbness_status,
          phlebitis: formData.phlebitis,
          suture_status: formData.suture_status,
          other_symptoms: formData.other_symptoms,
          other_symptoms_custom: formData.other_symptoms_custom,
          antibiotic_compliance: formData.antibiotic_compliance,
          compress_type: formData.compress_type,
          imf_wire_status: formData.imf_wire_status,
          walking_status: formData.walking_status,
          brushing_teeth: formData.brushing_teeth,
          mouth_rinsing: formData.mouth_rinsing,
          food_types: formData.food_types,
          food_types_custom: formData.food_types_custom,
          food_amount: formData.food_amount,
          ng_tube_position: formData.ng_tube_position,
        },
        custom_symptoms: formData.other_symptoms_custom?.map((c: any) =>
          [c.symptom?.trim(), c.detail?.trim()].filter(Boolean).join(': ')
        ).filter(Boolean) || [],
        additional_questions: formData.additional_questions,
        language: lang,
        ...(scheduleDate ? { submitted_at: new Date(scheduleDate).toISOString() } : {}),
      })
      setIsSuccess(true)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      if (msg === 'รหัสผ่านไม่ถูกต้อง') {
        setUnlocked(false)
        setUnlockError('รหัสผ่านหมดอายุหรือไม่ถูกต้อง กรุณากรอกรหัสใหม่อีกครั้ง')
      } else {
        setSubmitError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง')
      }
      setIsSubmitting(false)
    }
  }

  let symptomsCount = 11
  if ((formData.pain_score || 0) > 0) symptomsCount++
  if (formData.imf_wire || formData.imf_elastic) symptomsCount++
  if (formData.special_icbg) symptomsCount++
  const dailyLifeStartNum = 13 + symptomsCount

  const LangToggle = () => (
    <button
      onClick={() => setLang(l => l === 'th' ? 'en' : 'th')}
      className="text-xs font-medium px-2.5 py-1 rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors"
    >
      {ui.langToggle}
    </button>
  )

  // ── Loading / Error screens ──────────────────────────────────────────────────

  if (tokenLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    )
  }

  if (tokenError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-sm p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{ui.errorTitle}</h2>
          <p className="text-gray-600">{tokenError}</p>
        </div>
      </div>
    )
  }

  // ── Password gate ────────────────────────────────────────────────────────────

  if (!unlocked) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-sm p-8 max-w-sm w-full">
          <div className="flex justify-end mb-2">
            <LangToggle />
          </div>
          <div className="w-14 h-14 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-7 h-7" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 text-center mb-1">{ui.lockTitle}</h2>
          <p className="text-sm text-gray-500 text-center mb-6">{ui.lockSubtitle}</p>
          <div className="space-y-3">
            <input
              type="text"
              inputMode="text"
              maxLength={6}
              placeholder="xxxxxx"
              value={password}
              onChange={e => setPassword(e.target.value.replace(/[^a-zA-Z0-9]/g, ''))}
              onKeyDown={e => e.key === 'Enter' && handleUnlock()}
              className="input text-center text-2xl font-mono tracking-widest w-full"
              autoFocus
            />
            {unlockError && (
              <p className="text-sm text-red-600 text-center">{unlockError}</p>
            )}
            <button
              onClick={handleUnlock}
              disabled={password.length !== 6 || unlocking}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {unlocking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
              {unlocking ? ui.unlocking : ui.unlockBtn}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── Success screen ───────────────────────────────────────────────────────────

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-sm p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{ui.successTitle}</h2>
          <p className="text-gray-600">
            {ui.successMsg}<br />
            {ui.successLine.replace('LINE OA', '')} <b>LINE OA</b>
            {lang === 'th' ? ' อีกครั้ง' : ''}
          </p>
        </div>
      </div>
    )
  }

  // ── Form ─────────────────────────────────────────────────────────────────────

  const renderStep = () => {
    switch (currentStep) {
      case 1: return (
        <PatientConfirmStep data={formData} lang={lang} onReady={setIsCurrentStepValid} />
      )
      case 2: return (
        <SymptomsForm data={formData} onChange={handleFormDataChange} onValidationChange={setIsCurrentStepValid} startingQuestionNumber={13} lang={lang} />
      )
      case 3: return (
        <DailyLifeForm data={formData} onChange={handleFormDataChange} onValidationChange={setIsCurrentStepValid} startingQuestionNumber={dailyLifeStartNum} lang={lang} />
      )
      default: return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between gap-2">
          <div className="min-w-0">
            <h1 className="font-semibold text-gray-900 text-sm truncate">{ui.formTitle}</h1>
            {patientName && (
              <p className="text-xs text-gray-400 mt-0.5">
                {ui.patient} {patientName}
                {scheduleDate && ` | ${ui.schedule} ${new Date(scheduleDate).toLocaleDateString(lang === 'th' ? 'th-TH' : 'en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}`}
              </p>
            )}
          </div>
          <LangToggle />
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6">
        <div className="flex items-center justify-center gap-2 mb-6">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex flex-col items-center ${currentStep === step.id ? 'text-primary font-bold' : 'text-gray-400'}`}>
                <div className={`w-9 h-9 flex items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors ${
                  currentStep === step.id ? 'border-primary bg-primary text-white'
                    : currentStep > step.id ? 'border-green-500 bg-green-500 text-white'
                    : 'border-gray-300 bg-white text-gray-400'
                }`}>
                  {currentStep > step.id ? <CheckCircle className="w-4 h-4" /> : step.id}
                </div>
                <span className="mt-1 text-xs text-center max-w-[100px]">{step.title}</span>
              </div>
              {index < STEPS.length - 1 && (
                <div className={`h-0.5 w-8 mx-2 transition-colors ${currentStep > step.id ? 'bg-green-500' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          {renderStep()}
        </div>

        {submitError && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm text-center">
            {submitError}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 mt-6">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="btn-outline flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="w-4 h-4" /> {ui.prev}
          </button>
          {currentStep < STEPS.length ? (
            <button
              onClick={handleNext}
              disabled={!isCurrentStepValid}
              className="btn-primary flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {ui.next} <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!isCurrentStepValid || isSubmitting}
              className="btn-primary flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isSubmitting
                ? <><Loader2 className="w-4 h-4 animate-spin" /> {ui.submitting}</>
                : <><CheckCircle className="w-4 h-4" /> {ui.submit}</>}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function PublicFormPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>}>
      <PublicFormContent />
    </Suspense>
  )
}
