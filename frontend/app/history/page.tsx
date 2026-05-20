'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Search } from 'lucide-react'
import Navbar from '@/components/layout/Navbar'
import RiskBadge from '@/components/ui/RiskBadge'
import Spinner from '@/components/ui/Spinner'
import { getMe, listAssessments } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import { getHomeRoute } from '@/lib/routing'
import type { Assessment } from '@/lib/types'

function fmt(iso: string) {
  return new Date(iso).toLocaleString('th-TH', { dateStyle: 'short', timeStyle: 'short' })
}

export default function HistoryPage() {
  const router = useRouter()
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const PAGE_SIZE = 20

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    if (page === 0) {
      getMe().then(u => {
        if (!u.roles?.includes('view_cases') && !u.roles?.includes('view_all_cases')) router.push(getHomeRoute(u))
        else load()
      }).catch(() => { if (!isLoggedIn()) router.push('/login') })
    } else {
      load()
    }
  }, [page])

  const load = async () => {
    setLoading(true)
    try {
      const data = await listAssessments({ skip: page * PAGE_SIZE, limit: PAGE_SIZE })
      setAssessments(data)
    } finally {
      setLoading(false)
    }
  }

  const filtered = assessments.filter((a) =>
    !search || a.patient_hn.includes(search)
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-screen-xl mx-auto px-4 py-6">
        <h1 className="text-xl font-semibold text-gray-800 mb-2">ประวัติย้อนหลัง</h1>
        <p className="text-sm text-gray-500 mb-4">บันทึกการประเมินทั้งหมดในระบบ</p>

        <div className="card mb-4">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input pl-9"
              placeholder="ค้นหาด้วย HN..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="card overflow-hidden p-0">
          {loading ? (
            <div className="flex justify-center py-12"><Spinner className="w-8 h-8" /></div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">#</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">HN</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">วันที่ประเมิน</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">ภาษา</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">ความเสี่ยง</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">ดูรายละเอียด</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.length === 0 ? (
                  <tr><td colSpan={6} className="text-center py-10 text-gray-400">ไม่พบข้อมูล</td></tr>
                ) : (
                  filtered.map((a, i) => {
                    const risk = (a as Assessment & { overall_risk?: string }).overall_risk
                    return (
                      <tr key={a.assessment_id} className="hover:bg-gray-50/50">
                        <td className="px-4 py-3 text-gray-400">{page * PAGE_SIZE + i + 1}</td>
                        <td className="px-4 py-3 font-mono">{a.patient_hn}</td>
                        <td className="px-4 py-3 text-gray-600">{fmt(a.submitted_at)}</td>
                        <td className="px-4 py-3">
                          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full">{a.language === 'th' ? 'ไทย' : 'EN'}</span>
                        </td>
                        <td className="px-4 py-3"><RiskBadge risk={risk} /></td>
                        <td className="px-4 py-3">
                          <Link href={`/patients/${a.patient_hn}?assessment=${a.assessment_id}`} className="text-primary hover:underline text-xs">
                            ดูรายละเอียด →
                          </Link>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          )}
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
            <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0} className="text-sm text-gray-500 disabled:opacity-40">← ก่อนหน้า</button>
            <span className="text-sm text-gray-400">หน้า {page + 1}</span>
            <button onClick={() => setPage(page + 1)} disabled={filtered.length < PAGE_SIZE} className="text-sm text-gray-500 disabled:opacity-40">ถัดไป →</button>
          </div>
        </div>
      </main>
    </div>
  )
}
