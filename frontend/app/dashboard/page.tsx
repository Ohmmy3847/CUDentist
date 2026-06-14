'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { AlertCircle, AlertTriangle, CheckCircle, ChevronRight, Plus, Search, User as UserIcon } from 'lucide-react'
import Navbar from '@/components/layout/Navbar'
import Pagination from '@/components/ui/Pagination'
import RiskBadge from '@/components/ui/RiskBadge'
import Spinner from '@/components/ui/Spinner'
import { getDashboardPatients, getDashboardStats, getMe } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import { getHomeRoute } from '@/lib/routing'
import type { DashboardPatient, DashboardStats, User } from '@/lib/types'

const RISK_FILTERS = [
  { label: 'ทั้งหมด', value: '' },
  { label: 'เสี่ยงต่ำ', value: 'ความเสี่ยงต่ำ' },
  { label: 'เสี่ยงกลาง', value: 'ความเสี่ยงกลาง' },
  { label: 'เสี่ยงสูง', value: 'ความเสี่ยงสูง' },
]

function formatDate(iso: string | null) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('th-TH', { dateStyle: 'short', timeStyle: 'short' })
}

function getPatientStatus(p: DashboardPatient): { label: string; className: string } {
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const hasFuture = (p.follow_up_schedules ?? []).some(d => new Date(d) >= today)
  if (!hasFuture) return { label: 'เสร็จสิ้น', className: 'bg-gray-100 text-gray-500' }
  if (p.last_assessment_id) return { label: 'รอดำเนินการ', className: 'bg-blue-50 text-blue-600' }
  return { label: 'ค้างตอบ', className: 'bg-red-50 text-red-600 border border-red-200 font-semibold' }
}

function urgencyScore(p: DashboardPatient): number {
  const { label } = getPatientStatus(p)
  if (label === 'ค้างตอบ') {
    if (p.overall_risk === 'ความเสี่ยงสูง') return 0
    if (p.overall_risk === 'ความเสี่ยงกลาง') return 1
    return 2
  }
  if (p.needs_review) return 3
  if (label === 'รอดำเนินการ') return 4
  return 5
}


export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [patients, setPatients] = useState<DashboardPatient[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [me, setMe] = useState<User | null>(null)
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(25)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    getMe().then(u => {
      setMe(u)
      if (!u.roles?.includes('view_cases') && !u.roles?.includes('view_all_cases')) { router.push(getHomeRoute(u)); return }
      fetchData()
    }).catch(() => { if (!isLoggedIn()) router.push('/login') })
  }, [])

  useEffect(() => {
    setPage(1)
  }, [search, riskFilter])

  useEffect(() => {
    const t = setTimeout(() => fetchPatients(), 300)
    return () => clearTimeout(t)
  }, [search, riskFilter, page, perPage])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [s, res] = await Promise.all([getDashboardStats(), getDashboardPatients({ limit: perPage, skip: 0 })])
      setStats(s)
      setPatients([...res.patients].sort((a, b) => urgencyScore(a) - urgencyScore(b)))
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }

  const fetchPatients = async () => {
    const res = await getDashboardPatients({ search: search || undefined, risk: riskFilter || undefined, limit: perPage, skip: (page - 1) * perPage })
    setPatients([...res.patients].sort((a, b) => urgencyScore(a) - urgencyScore(b)))
    setTotal(res.total)
  }

  const high = stats?.risk_counts?.['ความเสี่ยงสูง'] ?? 0
  const medium = stats?.risk_counts?.['ความเสี่ยงกลาง'] ?? 0
  const low = stats?.risk_counts?.['ความเสี่ยงต่ำ'] ?? 0
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-screen-xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">ติดตามผู้ป่วย</h1>
            <p className="text-sm text-gray-500">ติดตามสถานะและอาการของผู้ป่วยหลังรับการรักษา</p>
          </div>
          {me?.roles?.includes('add_case') && (
            <Link href="/patients/new" className="btn-primary flex items-center gap-1.5">
              <Plus className="w-4 h-4" />
              เพิ่มผู้ป่วยใหม่
            </Link>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <div className="card flex items-center gap-3">
            <div className="bg-gray-100 rounded-full p-2">
              <UserIcon className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <div className="text-xs text-gray-500">ผู้ป่วยทั้งหมด</div>
              <div className="text-lg sm:text-2xl font-bold text-gray-800">{stats?.total_patients ?? '-'} คน</div>
            </div>
          </div>
          <div className="card flex items-center gap-3">
            <div className="bg-red-50 rounded-full p-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <div className="text-xs text-gray-500">เสี่ยงสูง</div>
              <div className="text-lg sm:text-2xl font-bold text-red-600">{high} คน</div>
            </div>
          </div>
          <div className="card flex items-center gap-3">
            <div className="bg-yellow-50 rounded-full p-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <div className="text-xs text-gray-500">เสี่ยงกลาง</div>
              <div className="text-lg sm:text-2xl font-bold text-yellow-600">{medium} คน</div>
            </div>
          </div>
          <div className="card flex items-center gap-3">
            <div className="bg-green-50 rounded-full p-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <div className="text-xs text-gray-500">เสี่ยงต่ำ</div>
              <div className="text-lg sm:text-2xl font-bold text-green-600">{low} คน</div>
            </div>
          </div>
        </div>

        {/* Search + Filter */}
        <div className="card mb-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                className="input pl-9"
                placeholder="ค้นหาชื่อผู้ป่วย เบอร์โทร หรือ HN..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {RISK_FILTERS.map((f) => (
                <button
                  key={f.value}
                  onClick={() => setRiskFilter(f.value)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    riskFilter === f.value
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="card overflow-hidden p-0 mb-0">
          {loading ? (
            <div className="flex justify-center py-12">
              <Spinner className="w-8 h-8" />
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">ระดับความเสี่ยง</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">HN</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">ชื่อ-นามสกุล</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">เบอร์โทร</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">หัตถการ</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">อัพเดทล่าสุด</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">สถานะ</th>
                  <th className="w-8" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {patients.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="text-center py-10 text-gray-400">ไม่พบข้อมูลผู้ป่วย</td>
                  </tr>
                ) : (
                  patients.map((p) => {
                    const status = getPatientStatus(p)
                    return (
                      <tr key={p.hn} className="hover:bg-gray-50/50 transition-colors">
                        <td className="px-4 py-3">
                          <RiskBadge risk={p.overall_risk} />
                        </td>
                        <td className="px-4 py-3 font-mono text-gray-700 text-xs sm:text-sm">{p.hn}</td>
                        <td className="px-4 py-3 font-medium text-gray-800 max-w-[120px] sm:max-w-none truncate">
                          {p.first_name} {p.last_name}
                        </td>
                        <td className="px-4 py-3 text-gray-600 hidden sm:table-cell">{p.phone || '-'}</td>
                        <td className="px-4 py-3 text-gray-600 hidden md:table-cell max-w-[180px] truncate">
                          {p.procedures?.join(', ') || '-'}
                        </td>
                        <td className="px-4 py-3 text-gray-500 hidden lg:table-cell text-xs">
                          {formatDate(p.last_assessment_at)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <span className={`text-xs px-2 py-0.5 rounded-full ${status.className}`}>
                              {status.label}
                            </span>
                            {p.line_user_id ? (
                              <span className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full">
                                LINE ✓
                              </span>
                            ) : p.line_reg_code ? (
                              <span className="text-xs bg-yellow-50 text-yellow-800 border border-yellow-200 px-2 py-0.5 rounded-full font-mono">
                                {p.line_reg_code}
                              </span>
                            ) : null}
                            {p.needs_review && (
                              <span title="รอตรวจสอบ AI" className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3 shrink-0" /> รอตรวจสอบ
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <Link href={`/patients/${p.hn}`} className="text-gray-400 hover:text-primary transition-colors">
                            <ChevronRight className="w-5 h-5" />
                          </Link>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          )}
          <Pagination page={page} perPage={perPage} total={total} onPageChange={setPage} onPerPageChange={(n) => { setPerPage(n); setPage(1) }} />
        </div>
      </main>
    </div>
  )
}
