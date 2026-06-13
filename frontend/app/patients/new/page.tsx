'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, ChevronRight, Clock, Plus, X } from 'lucide-react'
import Navbar from '@/components/layout/Navbar'
import Spinner from '@/components/ui/Spinner'
import { createPatient, getMe, listStaff } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import { PROCEDURE_OPTIONS } from '@/lib'

const TH_MONTHS = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
const TH_DAYS = ['อา', 'จ', 'อ', 'พ', 'พฤ', 'ศ', 'ส']

function toDateStr(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function formatThDate(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  return `${d.getDate()} ${TH_MONTHS[d.getMonth()]} ${d.getFullYear() + 543}`
}

// ─── Inline Calendar ──────────────────────────────────────────────────────────
interface CalendarProps {
  maxDates: number
  selectedDates: string[]
  onChange: (dates: string[]) => void
}

function InlineCalendar({ maxDates, selectedDates, onChange }: CalendarProps) {
  const today = new Date()
  const [viewYear, setViewYear] = useState(today.getFullYear())
  const [viewMonth, setViewMonth] = useState(today.getMonth())

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(y => y - 1) }
    else setViewMonth(m => m - 1)
  }
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(y => y + 1) }
    else setViewMonth(m => m + 1)
  }

  const firstDay = new Date(viewYear, viewMonth, 1).getDay()
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate()
  const cells: (number | null)[] = [
    ...Array(firstDay).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ]
  while (cells.length % 7 !== 0) cells.push(null)

  const handleDay = (day: number) => {
    const str = toDateStr(new Date(viewYear, viewMonth, day))
    if (selectedDates.includes(str)) {
      onChange(selectedDates.filter(s => s !== str))
    } else if (selectedDates.length < maxDates) {
      onChange([...selectedDates, str].sort())
    }
  }

  const thYear = viewYear + 543

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden w-full">
      {/* Month nav */}
      <div className="flex items-center justify-between bg-primary text-white px-4 py-2.5">
        <button type="button" onClick={prevMonth} className="p-1 rounded hover:bg-white/20 transition-colors">
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="font-medium text-sm">{TH_MONTHS[viewMonth]} {thYear}</span>
        <button type="button" onClick={nextMonth} className="p-1 rounded hover:bg-white/20 transition-colors">
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 bg-gray-50 border-b border-gray-100">
        {TH_DAYS.map(d => (
          <div key={d} className="text-center text-xs text-gray-500 font-medium py-2">{d}</div>
        ))}
      </div>

      {/* Date cells */}
      <div className="grid grid-cols-7 bg-white">
        {cells.map((day, i) => {
          if (!day) return <div key={i} className="py-2" />
          const str = toDateStr(new Date(viewYear, viewMonth, day))
          const selected = selectedDates.includes(str)
          const isPast = new Date(viewYear, viewMonth, day) < new Date(today.getFullYear(), today.getMonth(), today.getDate())
          const atLimit = !selected && selectedDates.length >= maxDates

          return (
            <button
              key={i}
              type="button"
              disabled={isPast || atLimit}
              onClick={() => handleDay(day)}
              className={`py-2 text-sm font-medium transition-all mx-0.5 rounded-lg
                ${isPast ? 'text-gray-300 cursor-default' : ''}
                ${atLimit && !selected ? 'text-gray-300 cursor-not-allowed' : ''}
                ${selected ? 'bg-primary text-white shadow-sm' : ''}
                ${!selected && !isPast && !atLimit ? 'text-gray-700 hover:bg-primary/10' : ''}
              `}
            >
              {day}
            </button>
          )
        })}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 text-xs text-gray-500">
        เลือกแล้ว {selectedDates.length}/{maxDates} วัน
        {selectedDates.length >= maxDates && (
          <span className="ml-2 text-primary">ครบแล้ว — คลิกวันที่เลือกไว้เพื่อยกเลิก</span>
        )}
      </div>
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function NewPatientPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [customSymptoms, setCustomSymptoms] = useState<string[]>([''])
  const [selectedProcedures, setSelectedProcedures] = useState<string[]>([])
  const [lefortSub, setLefortSub] = useState<string[]>([])
  const [bssroSub, setBssroSub] = useState<string[]>([])
  const [biopsySub, setBiopsySub] = useState<string[]>([])
  const [staff, setStaff] = useState<{ user_id: number; full_name: string }[]>([])
  const [nurseQuery, setNurseQuery] = useState('')
  const [nurseOpen, setNurseOpen] = useState(false)

  const toggleSub = (list: string[], setList: (v: string[]) => void, val: string) =>
    setList(list.includes(val) ? list.filter(x => x !== val) : [...list, val])

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    getMe().then(u => {
      if (!u.roles?.includes('add_case')) { router.push('/login'); return }
    }).catch(() => router.push('/login'))
  }, [])

  useEffect(() => { listStaff().then(setStaff).catch(() => { }) }, [])

  const [form, setForm] = useState({
    hn: '', first_name: '', last_name: '', gender: '',
    date_of_birth: '', phone: '', surgery_date: '', discharge_date: '',
    imf_wire: false, imf_wire_loops: '',
    imf_elastic: false, imf_elastic_loops: '',
    special_icbg: false, special_icbg_description: '',
    special_ng_tube: false, special_ng_tube_description: '',
    note: '',
    surgical_tooth_numbers: '',
    extraction_tooth_numbers: '',
    responsible_user_id: '' as string | number,
    // follow-up schedule
    follow_up_days: '1',
    follow_up_selected_dates: [] as string[],
    // time settings
    time_mode: 'same' as 'same' | 'per_day',
    follow_up_time: '08:00',
    per_day_times: {} as Record<string, string>,
  })

  const set = (k: string, v: unknown) => setForm(f => ({ ...f, [k]: v }))

  const maxDates = Math.max(1, parseInt(form.follow_up_days) || 1)

  // keep nurseQuery in sync when responsible_user_id is set programmatically
  useEffect(() => {
    if (!staff.length) return
    const id = Number(form.responsible_user_id || 0)
    if (!id) return
    const found = staff.find(s => s.user_id === id)
    if (found && nurseQuery !== found.full_name) setNurseQuery(found.full_name)
  }, [staff, form.responsible_user_id, nurseQuery])

  // When dates change, sync per_day_times keys
  const handleDatesChange = (dates: string[]) => {
    const newPerDay: Record<string, string> = {}
    dates.forEach(d => { newPerDay[d] = form.per_day_times[d] ?? '08:00' })
    setForm(f => ({ ...f, follow_up_selected_dates: dates, per_day_times: newPerDay }))
  }

  const setPerDayTime = (date: string, time: string) =>
    setForm(f => ({ ...f, per_day_times: { ...f.per_day_times, [date]: time } }))

  const toggleProcedure = (p: string) =>
    setSelectedProcedures(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p])

  const addCustomSymptom = () => setCustomSymptoms(prev => [...prev, ''])
  const updateCustomSymptom = (i: number, val: string) =>
    setCustomSymptoms(prev => prev.map((s, idx) => idx === i ? val : s))
  const removeCustomSymptom = (i: number) =>
    setCustomSymptoms(prev => prev.filter((_, idx) => idx !== i))

  const validate = () => {
    const nextErrors: Record<string, string> = {}
    const required = (key: string, value: string, label: string) => {
      if (!value.trim()) nextErrors[key] = `กรุณากรอก${label}`
    }

    // Patient Information (all required)
    required('hn', form.hn, 'HN')
    required('first_name', form.first_name, 'ชื่อ')
    required('last_name', form.last_name, 'นามสกุล')
    required('gender', form.gender, 'เพศ')
    required('phone', form.phone, 'เบอร์โทร')
    required('date_of_birth', form.date_of_birth, 'วันเกิด')
    required('surgery_date', form.surgery_date, 'วันที่ผ่าตัด')
    required('discharge_date', form.discharge_date, 'วัน Discharge')
    if (!form.responsible_user_id) nextErrors.responsible_user_id = 'กรุณาเลือกพยาบาลผู้รับผิดชอบ'

    // Procedures required (standard + additional)
    const additionalProcedures = customSymptoms.map(s => s.trim()).filter(Boolean)
    if (selectedProcedures.length + additionalProcedures.length === 0) {
      nextErrors.procedures = 'กรุณาเลือกหัตถการอย่างน้อย 1 รายการ'
    }

    // Follow-up schedules required
    const requiredDates = Math.max(1, parseInt(form.follow_up_days) || 1)
    if (form.follow_up_selected_dates.length !== requiredDates) {
      nextErrors.follow_up_selected_dates = `กรุณาเลือกวันติดตามอาการให้ครบ ${requiredDates} วัน`
    }

    setFieldErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setFieldErrors({})
    if (!validate()) return
    setLoading(true)
    try {
      let followUpDateIso: string | undefined = undefined
      let followUpSchedules: string[] | undefined = undefined

      if (form.follow_up_selected_dates.length > 0) {
        followUpSchedules = form.follow_up_selected_dates.map(date => {
          const time = form.time_mode === 'same' ? form.follow_up_time : form.per_day_times[date] || '08:00'
          return new Date(`${date}T${time}:00`).toISOString()
        })
        followUpDateIso = followUpSchedules[0]
      }

      const additionalProcedures = customSymptoms.map(s => s.trim()).filter(Boolean)
      const procedures = [...selectedProcedures, ...additionalProcedures]

      await createPatient({
        hn: form.hn, first_name: form.first_name, last_name: form.last_name,
        gender: form.gender || undefined, date_of_birth: form.date_of_birth || undefined,
        phone: form.phone || undefined, procedures,
        follow_up_date: followUpDateIso,
        follow_up_schedules: followUpSchedules,
        responsible_user_id: form.responsible_user_id ? Number(form.responsible_user_id) : undefined,
        extra_info: {
          surgery_date: form.surgery_date || null,
          discharge_date: form.discharge_date || null,
          note: form.note || null,
          imf_wire: form.imf_wire,
          imf_wire_loops: form.imf_wire_loops ? Number(form.imf_wire_loops) : null,
          imf_elastic: form.imf_elastic,
          imf_elastic_loops: form.imf_elastic_loops ? Number(form.imf_elastic_loops) : null,
          special_icbg: form.special_icbg,
          special_icbg_description: form.special_icbg_description || null,
          special_ng_tube: form.special_ng_tube,
          special_ng_tube_description: form.special_ng_tube_description || null,
          lefort_sub_options: lefortSub,
          bssro_sub_options: bssroSub,
          biopsy_sub_options: biopsySub,
          surgical_tooth_numbers: form.surgical_tooth_numbers || null,
          extraction_tooth_numbers: form.extraction_tooth_numbers || null,
        },
      })
      // Assessment will be created when patient submits the form via LINE OA
      router.push(`/patients/${form.hn}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-6">
        <button onClick={() => router.back()} className="flex items-center gap-1 text-sm text-gray-500 hover:text-primary mb-4 transition-colors">
          <ChevronLeft className="w-4 h-4" /> กลับ
        </button>

        <form onSubmit={submit} className="space-y-6">
          {/* ─── Basic info ─── */}
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-4">ข้อมูลผู้ป่วย</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="label">HN <span className="text-red-500">*</span></label>
                <input className={`input ${fieldErrors.hn ? 'border-red-300 focus:border-red-400' : ''}`} value={form.hn} onChange={e => set('hn', e.target.value)} required />
                {fieldErrors.hn && <p className="text-xs text-red-500 mt-1">{fieldErrors.hn}</p>}
              </div>
              <div>
                <label className="label">เพศ <span className="text-red-500">*</span></label>
                <input
                  className={`input ${fieldErrors.gender ? 'border-red-300 focus:border-red-400' : ''}`}
                  list="gender-options"
                  placeholder="เลือกหรือพิมพ์เองได้"
                  value={form.gender}
                  onChange={e => set('gender', e.target.value)}
                  required
                />
                <datalist id="gender-options">
                  <option value="ชาย" />
                  <option value="หญิง" />
                </datalist>
                {fieldErrors.gender && <p className="text-xs text-red-500 mt-1">{fieldErrors.gender}</p>}
              </div>
              <div>
                <label className="label">ชื่อ <span className="text-red-500">*</span></label>
                <input className={`input ${fieldErrors.first_name ? 'border-red-300 focus:border-red-400' : ''}`} value={form.first_name} onChange={e => set('first_name', e.target.value)} required />
                {fieldErrors.first_name && <p className="text-xs text-red-500 mt-1">{fieldErrors.first_name}</p>}
              </div>
              <div>
                <label className="label">นามสกุล <span className="text-red-500">*</span></label>
                <input className={`input ${fieldErrors.last_name ? 'border-red-300 focus:border-red-400' : ''}`} value={form.last_name} onChange={e => set('last_name', e.target.value)} required />
                {fieldErrors.last_name && <p className="text-xs text-red-500 mt-1">{fieldErrors.last_name}</p>}
              </div>
              <div>
                <label className="label">เบอร์โทร <span className="text-red-500">*</span></label>
                <input
                  className={`input ${fieldErrors.phone ? 'border-red-300 focus:border-red-400' : ''}`}
                  type="tel"
                  inputMode="numeric"
                  maxLength={12}
                  placeholder="xxx-xxx-xxxx"
                  value={form.phone}
                  onChange={e => {
                    const digits = e.target.value.replace(/\D/g, '').slice(0, 10)
                    const formatted = digits.length <= 3 ? digits
                      : digits.length <= 6 ? `${digits.slice(0, 3)}-${digits.slice(3)}`
                        : `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`
                    set('phone', formatted)
                  }}
                  required
                />
                {fieldErrors.phone && <p className="text-xs text-red-500 mt-1">{fieldErrors.phone}</p>}
              </div>
              <div>
                <label className="label">วันเกิด <span className="text-red-500">*</span></label>
                <input type="date" className="input" value={form.date_of_birth}
                  max={new Date().toISOString().slice(0, 10)}
                  onChange={e => {
                    set('date_of_birth', e.target.value)
                    if (form.surgery_date && e.target.value > form.surgery_date) set('surgery_date', '')
                  }} required />
                {fieldErrors.date_of_birth && <p className="text-xs text-red-500 mt-1">{fieldErrors.date_of_birth}</p>}
              </div>
              <div>
                <label className="label">วันที่ผ่าตัด <span className="text-red-500">*</span></label>
                <input type="date" className="input" value={form.surgery_date}
                  min={form.date_of_birth || undefined}
                  max={new Date().toISOString().slice(0, 10)}
                  onChange={e => {
                    set('surgery_date', e.target.value)
                    if (form.discharge_date && e.target.value > form.discharge_date) set('discharge_date', '')
                  }} required />
                {fieldErrors.surgery_date && <p className="text-xs text-red-500 mt-1">{fieldErrors.surgery_date}</p>}
              </div>
              <div>
                <label className="label">วัน Discharge <span className="text-red-500">*</span></label>
                <input type="date" className={`input ${fieldErrors.discharge_date ? 'border-red-300 focus:border-red-400' : ''}`} value={form.discharge_date}
                  min={form.surgery_date || form.date_of_birth || undefined}
                  onChange={e => set('discharge_date', e.target.value)} required />
                {fieldErrors.discharge_date && <p className="text-xs text-red-500 mt-1">{fieldErrors.discharge_date}</p>}
              </div>
              <div>
                <label className="label">พยาบาลผู้รับผิดชอบ <span className="text-red-500">*</span></label>
                <div className="relative">
                  <input
                    className={`input ${fieldErrors.responsible_user_id ? 'border-red-300 focus:border-red-400' : ''}`}
                    placeholder="พิมพ์เพื่อค้นหา..."
                    value={nurseQuery}
                    onChange={e => {
                      setNurseQuery(e.target.value)
                      set('responsible_user_id', '')
                      setNurseOpen(true)
                    }}
                    onFocus={() => setNurseOpen(true)}
                    onBlur={() => setTimeout(() => {
                      setNurseOpen(false)
                      if (!form.responsible_user_id && nurseQuery.trim()) {
                        const q = nurseQuery.toLowerCase().trim()
                        const exact = staff.find(s => s.full_name.toLowerCase() === q)
                        if (exact) {
                          set('responsible_user_id', exact.user_id)
                          setNurseQuery(exact.full_name)
                        } else {
                          const partial = staff.find(s => s.full_name.toLowerCase().includes(q))
                          if (partial) {
                            set('responsible_user_id', partial.user_id)
                            setNurseQuery(partial.full_name)
                          } else {
                            setNurseQuery('')
                          }
                        }
                      }
                    }, 150)}
                    required
                  />
                  {nurseOpen && staff.length > 0 && (
                    <div className="absolute z-10 mt-1 w-full max-h-56 overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg">
                      {staff
                        .filter(s => s.full_name.toLowerCase().includes(nurseQuery.toLowerCase().trim()))
                        .slice(0, 50)
                        .map(s => (
                          <button
                            key={s.user_id}
                            type="button"
                            className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => {
                              set('responsible_user_id', s.user_id)
                              setNurseQuery(s.full_name)
                              setNurseOpen(false)
                            }}
                          >
                            {s.full_name}
                          </button>
                        ))}
                      {staff.filter(s => s.full_name.toLowerCase().includes(nurseQuery.toLowerCase().trim())).length === 0 && (
                        <div className="px-3 py-2 text-sm text-gray-500">ไม่พบรายชื่อ</div>
                      )}
                    </div>
                  )}
                </div>
                {fieldErrors.responsible_user_id && <p className="text-xs text-red-500 mt-1">{fieldErrors.responsible_user_id}</p>}
              </div>
            </div>
          </div>

          {/* ─── Procedures ─── */}
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-1">หัตถการ <span className="text-red-500">*</span></h2>
            <p className="text-xs text-gray-400 mb-3">เลือกได้มากกว่า 1 อย่าง</p>
            {fieldErrors.procedures && <p className="text-sm text-red-600 mb-2">{fieldErrors.procedures}</p>}
            <div className="space-y-3">
              {PROCEDURE_OPTIONS.map(proc => {
                const isLefort = proc.includes('Lefort I')
                const isBSSRO = proc.includes('BSSRO')
                const isBiopsy = proc.includes('Biopsy')
                const isSurgicalRemoval = proc.includes('ผ่าตัดถอนฟัน')
                const isExtraction = proc.includes('ถอนฟัน') && !isSurgicalRemoval
                const checked = selectedProcedures.includes(proc)
                return (
                  <div key={proc}>
                    <label className="flex items-start gap-2 cursor-pointer">
                      <input type="checkbox" className="accent-primary w-4 h-4 mt-0.5" checked={checked} onChange={() => toggleProcedure(proc)} />
                      <span className="text-sm text-gray-700">{proc}</span>
                    </label>
                    {isLefort && checked && (
                      <div className="ml-6 mt-2 flex flex-wrap gap-2">
                        {['Advancement', 'Setback', 'Osteotomy', '2 pieces', 'Impaction'].map(opt => (
                          <label key={opt} className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs border cursor-pointer transition-colors ${lefortSub.includes(opt) ? 'bg-blue-100 border-blue-400 text-blue-800' : 'bg-white border-blue-200 text-gray-600 hover:bg-blue-50'}`}>
                            <input type="checkbox" className="sr-only" checked={lefortSub.includes(opt)} onChange={() => toggleSub(lefortSub, setLefortSub, opt)} />
                            {opt}
                          </label>
                        ))}
                      </div>
                    )}
                    {isBSSRO && checked && (
                      <div className="ml-6 mt-2 flex flex-wrap gap-2">
                        {['Setback', 'Advancement'].map(opt => (
                          <label key={opt} className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs border cursor-pointer transition-colors ${bssroSub.includes(opt) ? 'bg-green-100 border-green-400 text-green-800' : 'bg-white border-green-200 text-gray-600 hover:bg-green-50'}`}>
                            <input type="checkbox" className="sr-only" checked={bssroSub.includes(opt)} onChange={() => toggleSub(bssroSub, setBssroSub, opt)} />
                            {opt}
                          </label>
                        ))}
                      </div>
                    )}
                    {isBiopsy && checked && (
                      <div className="ml-6 mt-2 flex flex-wrap gap-2">
                        {['Excisional', 'Incisional'].map(opt => (
                          <label key={opt} className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs border cursor-pointer transition-colors ${biopsySub.includes(opt) ? 'bg-pink-100 border-pink-400 text-pink-800' : 'bg-white border-pink-200 text-gray-600 hover:bg-pink-50'}`}>
                            <input type="checkbox" className="sr-only" checked={biopsySub.includes(opt)} onChange={() => toggleSub(biopsySub, setBiopsySub, opt)} />
                            {opt}
                          </label>
                        ))}
                      </div>
                    )}
                    {isSurgicalRemoval && checked && (
                      <div className="ml-6 mt-2">
                        <input className="input w-48 text-sm" placeholder="หมายเลขซี่ฟัน เช่น 18, 38" value={form.surgical_tooth_numbers}
                          onChange={e => set('surgical_tooth_numbers', e.target.value.replace(/[^0-9,\s]/g, ''))} />
                      </div>
                    )}
                    {isExtraction && checked && (
                      <div className="ml-6 mt-2">
                        <input className="input w-48 text-sm" placeholder="หมายเลขซี่ฟัน เช่น 18, 38" value={form.extraction_tooth_numbers}
                          onChange={e => set('extraction_tooth_numbers', e.target.value.replace(/[^0-9,\s]/g, ''))} />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100">
              <h3 className="font-medium text-gray-800 mb-2 text-sm">หัตถการ อื่นๆ (เพิ่มเติม)</h3>
              <div className="space-y-2 mb-3">
                {customSymptoms.map((s, i) => (
                  <div key={i} className="flex gap-2">
                    <input className="input flex-1" placeholder="ระบุหัตถการอื่นๆ..." value={s} onChange={e => updateCustomSymptom(i, e.target.value)} />
                    {customSymptoms.length > 1 && (
                      <button type="button" onClick={() => removeCustomSymptom(i)} className="text-red-400 hover:text-red-600">
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <button type="button" onClick={addCustomSymptom} className="flex items-center gap-1 text-primary text-sm hover:underline">
                <Plus className="w-4 h-4" /> เพิ่มหัตถการอื่นๆ
              </button>
            </div>
          </div>

          {/* ─── Special devices ─── */}
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-3">อุปกรณ์พิเศษ</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="accent-primary" checked={form.imf_wire} onChange={e => set('imf_wire', e.target.checked)} />
                  <span className="text-sm font-medium">IMF ลวด</span>
                </label>
                {form.imf_wire && <input className="input" type="number" placeholder="จำนวน loop (1-10)" value={form.imf_wire_loops} onChange={e => set('imf_wire_loops', e.target.value)} />}
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="accent-primary" checked={form.special_icbg} onChange={e => set('special_icbg', e.target.checked)} />
                  <span className="text-sm font-medium">ICBG</span>
                </label>
                {form.special_icbg && <input className="input" placeholder="สำหรับเพิ่มเติม" value={form.special_icbg_description} onChange={e => set('special_icbg_description', e.target.value)} />}
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="accent-primary" checked={form.imf_elastic} onChange={e => set('imf_elastic', e.target.checked)} />
                  <span className="text-sm font-medium">IMF ยาง</span>
                </label>
                {form.imf_elastic && <input className="input" type="number" placeholder="จำนวน loop (1-10)" value={form.imf_elastic_loops} onChange={e => set('imf_elastic_loops', e.target.value)} />}
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="accent-primary" checked={form.special_ng_tube} onChange={e => set('special_ng_tube', e.target.checked)} />
                  <span className="text-sm font-medium">NG Tube</span>
                </label>
                {form.special_ng_tube && <input className="input" placeholder="สำหรับเพิ่มเติม" value={form.special_ng_tube_description} onChange={e => set('special_ng_tube_description', e.target.value)} />}
              </div>
            </div>
          </div>

          {/* ─── Note ─── */}
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-1">หมายเหตุพิเศษ</h2>
            <p className="text-xs text-gray-400 mb-4">หมายเหตุสำหรับแพทย์หรือพยาบาล</p>
            <textarea
              className="input h-24 resize-none"
              placeholder="เช่น แพ้ยา, เลือดออกมากผิดปกติ..."
              value={form.note}
              onChange={e => set('note', e.target.value)}
            />
          </div>

          {/* ─── Assessment settings ─── */}
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-5">ตั้งค่าการติดตามอาการ</h2>

            {/* Row 1: days */}
            <div className="mb-6">
              <label className="label">จำนวนวันติดตามอาการ <span className="text-red-500">*</span></label>
              <div className="flex items-center gap-2">
                <input
                  type="number" min="1" max="30"
                  className="input w-20 text-center"
                  value={form.follow_up_days}
                  onChange={e => {
                    set('follow_up_days', e.target.value)
                    const n = parseInt(e.target.value) || 1
                    if (form.follow_up_selected_dates.length > n) {
                      handleDatesChange(form.follow_up_selected_dates.slice(0, n))
                    }
                  }}
                />
                <span className="text-sm text-gray-500">วัน</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">เลือกได้ {maxDates} วันจากปฏิทิน</p>
              {fieldErrors.follow_up_selected_dates && <p className="text-xs text-red-500 mt-1">{fieldErrors.follow_up_selected_dates}</p>}
            </div>

            {/* Row 2: Calendar */}
            <div className="mb-6">
              <label className="label mb-2">
                เลือกวันที่ติดตามอาการจากปฏิทิน
                <span className="text-gray-400 font-normal ml-1">(คลิกเลือกได้อิสระ ไม่ต้องต่อเนื่อง)</span>
              </label>
              <InlineCalendar
                maxDates={maxDates}
                selectedDates={form.follow_up_selected_dates}
                onChange={handleDatesChange}
              />
            </div>

            {/* Row 3: Time settings — only show once dates are selected */}
            {form.follow_up_selected_dates.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Clock className="w-4 h-4 text-primary" />
                  <label className="label mb-0">เวลาที่ต้องการรับแจ้ง</label>
                </div>

                {/* Toggle */}
                <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit mb-4">
                  {([
                    { value: 'same', label: 'เวลาเดียวกันทุกวัน' },
                    { value: 'per_day', label: 'กำหนดแต่ละวัน' },
                  ] as const).map(opt => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => set('time_mode', opt.value)}
                      className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${form.time_mode === opt.value
                        ? 'bg-white text-primary shadow-sm'
                        : 'text-gray-500 hover:text-gray-700'
                        }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>

                {form.time_mode === 'same' ? (
                  /* Same time for all */
                  <div className="flex items-center gap-3">
                    <input
                      type="time"
                      className="input w-36"
                      value={form.follow_up_time}
                      onChange={e => set('follow_up_time', e.target.value)}
                    />
                    <span className="text-sm text-gray-500">
                      ใช้กับทุกวัน ({form.follow_up_selected_dates.length} วัน)
                    </span>
                  </div>
                ) : (
                  /* Per-day time */
                  <div className="space-y-2">
                    {form.follow_up_selected_dates.map(date => (
                      <div key={date} className="flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2">
                        <span className="text-sm text-gray-700 w-40 shrink-0">{formatThDate(date)}</span>
                        <input
                          type="time"
                          className="input w-32"
                          value={form.per_day_times[date] ?? '08:00'}
                          onChange={e => setPerDayTime(date, e.target.value)}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

          </div>

          {error && <p className="text-red-500 text-sm bg-red-50 px-4 py-2 rounded-lg">{error}</p>}

          <div className="flex gap-3 justify-end pb-6">
            <button type="button" onClick={() => router.back()} className="btn-outline">ยกเลิก</button>
            <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
              {loading && <Spinner className="w-4 h-4" />}
              {loading ? 'กำลังประมวลผล AI...' : 'บันทึก'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
