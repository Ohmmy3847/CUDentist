'use client'

import { Suspense, useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowLeft, ArrowRight, CheckCircle, Loader2 } from 'lucide-react'
import type { PatientFormData } from '@/lib'
import { th } from '@/lib/locales'
import BasicInfoForm from '@/components/forms/BasicInfoForm'
import SymptomsForm from '@/components/forms/SymptomsForm'
import DailyLifeForm from '@/components/forms/DailyLifeForm'
import { createAssessment, getPatient } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'

const STEPS = [
  { id: 1, title: th.form.steps.basicInfo, description: th.form.steps.description[1] },
  { id: 2, title: th.form.steps.symptoms, description: th.form.steps.description[2] },
  { id: 3, title: th.form.steps.dailyLife, description: th.form.steps.description[3] },
]

function NewAssessmentContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const hn = searchParams.get('hn') ?? ''
  const scheduleDateStr = searchParams.get('schedule') ?? ''

  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<PatientFormData>({})
  const [isCurrentStepValid, setIsCurrentStepValid] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [patientName, setPatientName] = useState('')

  // Prefill patient basic info from backend
  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    if (!hn) return
    getPatient(hn).then(p => {
      setPatientName(`${p.first_name} ${p.last_name}`)
      setFormData(prev => ({
        ...prev,
        hn: p.hn,
        first_name: p.first_name,
        last_name: p.last_name,
        phone: p.phone ?? undefined,
        gender: p.gender ?? undefined,
        birth_date: p.date_of_birth ?? undefined,
        procedures: p.procedures ?? undefined,
      }))
    }).catch(() => {/* patient not found, let user fill manually */})
  }, [hn])

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
    setError(null)
    try {
      await createAssessment({
        patient_hn: hn || (formData.hn ?? ''),
        basic_info: {
          hn: formData.hn,
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
        additional_questions: formData.additional_questions,
        language: 'th',
        ...(scheduleDateStr ? { submitted_at: new Date(scheduleDateStr).toISOString() } : {}),
      })
      setIsSuccess(true)
      // If opened as popup by nurse, reload parent.
      if (window.opener) {
        window.opener.location.reload()
      }
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'เกิดข้อผิดพลาด — ตรวจสอบว่า Risk Service กำลังทำงาน')
      setIsSubmitting(false)
    }
  }

  // Count symptom questions for DailyLifeForm numbering
  let symptomsCount = 11
  if ((formData.pain_score || 0) > 0) symptomsCount++
  if (formData.imf_wire || formData.imf_elastic) symptomsCount++
  if (formData.special_icbg) symptomsCount++
  const dailyLifeStartNum = 13 + symptomsCount

  const renderStep = () => {
    switch (currentStep) {
      case 1: return (
        <BasicInfoForm
          data={formData}
          onChange={handleFormDataChange}
          onValidationChange={setIsCurrentStepValid}
          lang="th"
          isReadOnly={true}
        />
      )
      case 2: return (
        <SymptomsForm
          data={formData}
          onChange={handleFormDataChange}
          onValidationChange={setIsCurrentStepValid}
          startingQuestionNumber={13}
          lang="th"
        />
      )
      case 3: return (
        <DailyLifeForm
          data={formData}
          onChange={handleFormDataChange}
          onValidationChange={setIsCurrentStepValid}
          startingQuestionNumber={dailyLifeStartNum}
          lang="th"
        />
      )
      default: return null
    }
  }

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-sm p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">ส่งแบบประเมินสำเร็จ</h2>
          <p className="text-gray-600 mb-6">
            บันทึกข้อมูลของคุณเรียบร้อยแล้ว<br/>ผลการประเมินและคำแนะนำเพิ่มเติมจะถูกส่งแจ้งเตือนผ่านช่องทาง <b>Line OA</b> อีกครั้ง
          </p>
          <button
            onClick={() => window.close()}
            className="btn-primary w-full"
          >
            ปิดหน้าต่างนี้
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="font-semibold text-gray-900 text-sm">สร้างแบบประเมินใหม่</h1>
            {patientName && (
              <p className="text-xs text-gray-400 mt-0.5">
                ผู้ป่วย: {patientName} (HN: {hn})
                {scheduleDateStr && ` | กำหนดการ: ${new Date(scheduleDateStr).toLocaleDateString('th-TH', { day: '2-digit', month: 'short', year: 'numeric' })}`}
              </p>
            )}
          </div>
          <button
            onClick={() => window.close()}
            className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 px-3 py-1.5 rounded-lg"
          >
            ปิดหน้าต่าง
          </button>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-6">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex flex-col items-center ${currentStep === step.id ? 'text-primary font-bold' : 'text-gray-400'}`}>
                <div className={`w-9 h-9 flex items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors ${
                  currentStep === step.id
                    ? 'border-primary bg-primary text-white'
                    : currentStep > step.id
                    ? 'border-green-500 bg-green-500 text-white'
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

        {/* Form content */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          {renderStep()}
        </div>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm text-center">
            {error}
          </div>
        )}

        {/* Navigation */}
        <div className="grid grid-cols-2 gap-4 mt-6">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="btn-outline flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="w-4 h-4" /> ย้อนกลับ
          </button>

          {currentStep < STEPS.length ? (
            <button
              onClick={handleNext}
              disabled={!isCurrentStepValid}
              className="btn-primary flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              ถัดไป <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!isCurrentStepValid || isSubmitting}
              className="btn-primary flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> กำลังประมวลผล AI...</>
              ) : (
                <><CheckCircle className="w-4 h-4" /> ส่งและประเมิน</>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function NewAssessmentPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>}>
      <NewAssessmentContent />
    </Suspense>
  )
}
