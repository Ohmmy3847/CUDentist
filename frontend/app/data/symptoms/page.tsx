'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Pencil, Plus, RefreshCw, Search, Trash2 } from 'lucide-react'
import Pagination from '@/components/ui/Pagination'
import RiskBadge from '@/components/ui/RiskBadge'
import Spinner from '@/components/ui/Spinner'
import { createSymptom, deleteSymptom, listSymptoms, resyncSymptoms, updateSymptom } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import { getHomeRoute } from '@/lib/routing'
import type { Symptom } from '@/lib/types'

const RISK_OPTS = [
  { value: 'low', label: 'เสี่ยงต่ำ' },
  { value: 'medium', label: 'เสี่ยงกลาง' },
  { value: 'high', label: 'เสี่ยงสูง' },
  { value: 'complex', label: 'ซับซ้อน' },
]

const BLANK: Partial<Symptom> = { symptom_name: '', risk_level: 'low', recommendation: '', management_guidance: '', aliases: [] }

export default function SymptomsPage() {
  const router = useRouter()
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [modal, setModal] = useState<{ open: boolean; editing: Symptom | null; form: Partial<Symptom> }>({
    open: false, editing: null, form: BLANK,
  })
  const [saving, setSaving] = useState(false)
  const [resyncing, setResyncing] = useState(false)
  const [aliasInput, setAliasInput] = useState('')
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(25)

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    import('@/lib/api').then(({ getMe }) => getMe()).then(u => {
      if (!u.roles?.includes('manage_docs')) router.push(getHomeRoute(u))
      else load()
    }).catch(() => { if (!isLoggedIn()) router.push('/login') })
  }, [])

  const load = async () => {
    setLoading(true)
    const data = await listSymptoms()
    setSymptoms(data)
    setLoading(false)
  }

  const openNew = () => { setAliasInput(''); setModal({ open: true, editing: null, form: { ...BLANK } }) }
  const openEdit = (s: Symptom) => { setAliasInput(''); setModal({ open: true, editing: s, form: { ...s, aliases: s.aliases ?? [] } }) }

  const addAlias = () => {
    const v = aliasInput.trim()
    if (!v) return
    const current = modal.form.aliases ?? []
    if (!current.includes(v)) setModal(m => ({ ...m, form: { ...m.form, aliases: [...current, v] } }))
    setAliasInput('')
  }
  const removeAlias = (idx: number) =>
    setModal(m => ({ ...m, form: { ...m.form, aliases: (m.form.aliases ?? []).filter((_, i) => i !== idx) } }))
  const closeModal = () => setModal((m) => ({ ...m, open: false }))

  const save = async () => {
    setSaving(true)
    try {
      if (modal.editing) {
        await updateSymptom(modal.editing.symptom_id, modal.form)
      } else {
        await createSymptom(modal.form)
      }
      closeModal()
      await load()
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id: number) => {
    if (!confirm('ยืนยันการลบ?')) return
    await deleteSymptom(id)
    setSymptoms((prev) => prev.filter((s) => s.symptom_id !== id))
  }

  const handleResync = async () => {
    if (!confirm('Sync ข้อมูลอาการทั้งหมดไปยัง Vector DB ใหม่?')) return
    setResyncing(true)
    try {
      const res = await resyncSymptoms()
      alert(`Sync สำเร็จ ${res.count} อาการ`)
    } catch {
      alert('เกิดข้อผิดพลาด ไม่สามารถ sync ได้')
    } finally {
      setResyncing(false)
    }
  }

  const RISK_LABEL: Record<string, string> = { low: 'ความเสี่ยงต่ำ', medium: 'ความเสี่ยงกลาง', high: 'ความเสี่ยงสูง', complex: 'ซับซ้อน' }

  const filtered = symptoms.filter((s) => {
    const matchSearch = !search || s.symptom_name.includes(search) || (s.aliases ?? []).some(a => a.includes(search))
    const matchRisk = !riskFilter || s.risk_level === riskFilter
    return matchSearch && matchRisk
  })
  const paginated = filtered.slice((page - 1) * perPage, page * perPage)

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="font-semibold text-gray-800">ข้อมูลอาการอื่น ๆ (เพิ่มเติม)</h2>
          <p className="text-xs text-gray-400">จัดการกลุ่มคำที่ผู้ป่วยแจ้งและคำแนะนำสำหรับการเพิ่มเติมข้อมูลผู้ป่วย</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleResync}
            disabled={resyncing}
            className="flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors"
            title="Sync ข้อมูลทั้งหมดไปยัง Vector DB"
          >
            <RefreshCw className={`w-4 h-4 ${resyncing ? 'animate-spin' : ''}`} />
            Sync Vector DB
          </button>
          <button onClick={openNew} className="btn-primary flex items-center gap-1.5">
            <Plus className="w-4 h-4" /> เพิ่มอาการใหม่
          </button>
        </div>
      </div>

      <div className="card mb-4 flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input className="input pl-9" placeholder="ค้นหาชื่ออาการ..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="input max-w-[160px]" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
          <option value="">ทั้งหมด (รวมทุกความเสี่ยง)</option>
          {RISK_OPTS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>

      <div className="card overflow-hidden p-0">
        {loading ? (
          <div className="flex justify-center py-12"><Spinner className="w-8 h-8" /></div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">#</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">ชื่ออาการ</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">ความเสี่ยง</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">คำแนะนำ</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {paginated.length === 0 ? (
                <tr><td colSpan={5} className="text-center py-10 text-gray-400">ไม่พบข้อมูลอาการ</td></tr>
              ) : (
                paginated.map((s, i) => (
                  <tr key={s.symptom_id} className="hover:bg-gray-50/50">
                    <td className="px-4 py-3 text-gray-400">{(page - 1) * perPage + i + 1}</td>
                    <td className="px-4 py-3 font-medium text-gray-800">{s.symptom_name}</td>
                    <td className="px-4 py-3"><RiskBadge risk={RISK_LABEL[s.risk_level] || s.risk_level} /></td>
                    <td className="px-4 py-3 text-gray-600 max-w-[240px] truncate">{s.recommendation || '-'}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => openEdit(s)} className="text-gray-400 hover:text-primary transition-colors">
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button onClick={() => remove(s.symptom_id)} className="text-gray-400 hover:text-red-500 transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
        <Pagination page={page} perPage={perPage} total={filtered.length} onPageChange={setPage} onPerPageChange={(n) => { setPerPage(n); setPage(1) }} />
      </div>

      {/* Modal */}
      {modal.open && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="font-semibold text-gray-800">{modal.editing ? 'แก้ไขอาการ' : 'เพิ่มอาการใหม่'}</h2>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="label">ชื่ออาการ <span className="text-red-500">*</span></label>
                <div className="space-y-2">
                  <input className="input" value={modal.form.symptom_name || ''} onChange={(e) => setModal((m) => ({ ...m, form: { ...m.form, symptom_name: e.target.value } }))} placeholder="ชื่อหลัก" />
                  {(modal.form.aliases ?? []).map((a, i) => (
                    <div key={i} className="flex gap-2">
                      <input
                        className="input flex-1"
                        value={a}
                        onChange={(e) => setModal(m => ({ ...m, form: { ...m.form, aliases: (m.form.aliases ?? []).map((v, j) => j === i ? e.target.value : v) } }))}
                        placeholder={`ชื่ออาการที่ ${i + 2}`}
                      />
                      <button type="button" onClick={() => removeAlias(i)} className="text-gray-400 hover:text-red-500 px-2 transition-colors">×</button>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => setModal(m => ({ ...m, form: { ...m.form, aliases: [...(m.form.aliases ?? []), ''] } }))}
                    className="flex items-center gap-1.5 text-sm text-primary hover:text-primary/80 transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" /> เพิ่มชื่ออาการ
                  </button>
                </div>
              </div>
              <div>
                <label className="label">ระดับความเสี่ยง</label>
                <select className="input" value={modal.form.risk_level || 'low'} onChange={(e) => setModal((m) => ({ ...m, form: { ...m.form, risk_level: e.target.value } }))}>
                  {RISK_OPTS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </div>
              <div>
                <label className="label">คำแนะนำ</label>
                <textarea className="input resize-none" rows={2} value={modal.form.recommendation || ''} onChange={(e) => setModal((m) => ({ ...m, form: { ...m.form, recommendation: e.target.value } }))} />
              </div>
            </div>
            <div className="px-6 py-4 border-t border-gray-100 flex gap-3 justify-end">
              <button onClick={closeModal} className="btn-outline">ยกเลิก</button>
              <button onClick={save} disabled={saving} className="btn-primary flex items-center gap-2">
                {saving && <Spinner className="w-3 h-3" />}
                บันทึก
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
