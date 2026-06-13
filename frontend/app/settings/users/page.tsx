'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Pencil, Plus, Search, Trash2, X } from 'lucide-react'
import Pagination from '@/components/ui/Pagination'
import PasswordInput from '@/components/ui/PasswordInput'
import { createUser, deleteUser, getMe, listUsers, updateUser } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import { getHomeRoute } from '@/lib/routing'
import type { User } from '@/lib/types'


const PERMISSIONS = [
  { value: 'send_assessment', label: 'ส่งแบบประเมิน', desc: 'สร้างและส่งลิงก์แบบประเมินอาการให้ผู้ป่วย' },
  { value: 'view_cases', label: 'ดูเคสที่รับผิดชอบ', desc: 'เข้าถึง Dashboard ประวัติ และเคสที่ตนรับผิดชอบ — ชื่อจะขึ้นในช่องเลือกพยาบาลผู้รับผิดชอบ' },
  { value: 'view_all_cases', label: 'ดูเคสทั้งหมด', desc: 'ดูเคสผู้ป่วยทุกรายโดยไม่จำกัดผู้รับผิดชอบ (หัวหน้าพยาบาล)' },
  { value: 'add_case', label: 'เพิ่มเคสใหม่', desc: 'เพิ่มผู้ป่วยใหม่เข้าระบบ' },
  { value: 'edit_case', label: 'แก้ไขข้อมูลเคส', desc: 'แก้ไขข้อมูลผู้ป่วย เปลี่ยนผู้รับผิดชอบ' },
  { value: 'manage_users', label: 'จัดการบัญชีผู้ใช้', desc: 'เพิ่ม/ลบ/แก้ไขบัญชีและสิทธิ์ของเจ้าหน้าที่' },
  { value: 'manage_docs', label: 'จัดการเอกสาร', desc: 'อัปโหลดและจัดการเอกสารฐานความรู้ RAG' },
]

function AddUserModal({ onClose, onCreated, existingUsernames, isSuperuser }: { onClose: () => void; onCreated: (u: User) => void; existingUsernames: string[]; isSuperuser: boolean }) {
  const [form, setForm] = useState({ username: '', password: '', first_name: '', last_name: '', email: '', roles: ['send_assessment', 'view_cases', 'add_case', 'edit_case'] as string[] })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toggleRole = (role: string) => {
    setForm(f => ({
      ...f,
      roles: f.roles.includes(role) ? f.roles.filter(r => r !== role) : [...f.roles, role],
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (existingUsernames.includes(form.username)) { setError('ชื่อผู้ใช้นี้มีอยู่แล้ว'); return }
    if (form.roles.length === 0) { setError('กรุณาเลือกบทบาทอย่างน้อย 1 บทบาท'); return }
    setLoading(true)
    try {
      const user = await createUser({ ...form, email: form.email || undefined })
      onCreated(user)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'เกิดข้อผิดพลาด')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 shrink-0">
          <h2 className="font-semibold text-gray-900">เพิ่มบัญชีผู้ใช้ใหม่</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
          <div className="overflow-y-auto flex-1 p-5 space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">ชื่อ <span className="text-red-500">*</span></label>
                <input className="input w-full" value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))} required />
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">นามสกุล <span className="text-red-500">*</span></label>
                <input className="input w-full" value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))} required />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ชื่อผู้ใช้ <span className="text-red-500">*</span></label>
              <input className="input w-full" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} required autoComplete="off" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">อีเมล (สำหรับรีเซ็ตรหัสผ่าน)</label>
              <input type="email" className="input w-full" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} autoComplete="off" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">รหัสผ่านเริ่มต้น <span className="text-red-500">*</span></label>
              <PasswordInput className="input w-full" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} required minLength={6} autoComplete="new-password" />
              <p className="text-xs text-gray-400 mt-1">อย่างน้อย 6 ตัวอักษร — ผู้ใช้สามารถเปลี่ยนรหัสผ่านได้ภายหลัง</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">สิทธิ์การใช้งาน <span className="text-red-500">*</span></label>
              <div className="space-y-2">
                {PERMISSIONS.map(p => {
                  const locked = p.value === 'manage_users' && !isSuperuser
                  return (
                    <label key={p.value} className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${locked ? 'border-gray-100 bg-gray-50 cursor-not-allowed opacity-60' :
                        form.roles.includes(p.value) ? 'border-primary bg-primary/5 cursor-pointer' : 'border-gray-200 hover:border-gray-300 cursor-pointer'
                      }`}>
                      <input
                        type="checkbox"
                        className="mt-0.5 accent-primary"
                        checked={form.roles.includes(p.value)}
                        onChange={() => !locked && toggleRole(p.value)}
                        disabled={locked}
                      />
                      <div>
                        <div className="text-sm font-medium text-gray-800">{p.label}</div>
                        <div className="text-xs text-gray-400">{locked ? 'เฉพาะ superuser เท่านั้นที่กำหนดสิทธิ์นี้ได้' : p.desc}</div>
                      </div>
                    </label>
                  )
                })}
              </div>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>
          <div className="flex gap-3 px-5 py-4 border-t border-gray-100 shrink-0">
            <button type="button" onClick={onClose} className="btn btn-ghost flex-1">ยกเลิก</button>
            <button type="submit" className="btn btn-primary flex-1" disabled={loading}>
              {loading ? 'กำลังสร้าง...' : 'สร้างบัญชี'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function DeleteConfirmModal({ user, onCancel, onConfirm, loading }: {
  user: User
  onCancel: () => void
  onConfirm: () => void
  loading: boolean
}) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0">
            <Trash2 className="w-5 h-5 text-red-600" />
          </div>
          <h2 className="font-semibold text-gray-900">ลบบัญชีผู้ใช้</h2>
        </div>
        <p className="text-sm text-gray-600 mb-1">
          คุณกำลังจะลบบัญชีของ <span className="font-semibold text-gray-900">{user.first_name} {user.last_name}</span> ({user.username})
        </p>
        <p className="text-sm text-gray-500 mb-5">
          ผู้ใช้นี้จะไม่สามารถเข้าสู่ระบบได้อีก ข้อมูลที่บันทึกไว้จะยังคงอยู่ในระบบ
        </p>
        <div className="flex gap-3">
          <button onClick={onCancel} className="btn btn-ghost flex-1" disabled={loading}>
            ยกเลิก
          </button>
          <button onClick={onConfirm} className="flex-1 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-medium transition-colors disabled:opacity-50" disabled={loading}>
            {loading ? 'กำลังลบ...' : 'ลบบัญชี'}
          </button>
        </div>
      </div>
    </div>
  )
}

function EditUserModal({ user, onClose, onUpdated, isSuperuser }: {
  user: User
  onClose: () => void
  onUpdated: (u: User) => void
  isSuperuser: boolean
}) {
  const [form, setForm] = useState({
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email ?? '',
    roles: user.roles ?? [],
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toggle = (p: string) =>
    setForm(f => ({ ...f, roles: f.roles.includes(p) ? f.roles.filter(x => x !== p) : [...f.roles, p] }))

  const handleSave = async () => {
    setError('')
    if (form.roles.length === 0) { setError('กรุณาเลือกสิทธิ์อย่างน้อย 1 รายการ'); return }
    setLoading(true)
    try {
      const updated = await updateUser(user.user_id, {
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email || undefined,
        roles: form.roles,
      })
      onUpdated(updated)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 shrink-0">
          <div>
            <h2 className="font-semibold text-gray-900">แก้ไขข้อมูลผู้ใช้</h2>
            <p className="text-xs text-gray-400 mt-0.5">@{user.username}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
        </div>
        <div className="overflow-y-auto flex-1 p-5 space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">ชื่อ <span className="text-red-500">*</span></label>
              <input className="input w-full" value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))} required />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">นามสกุล <span className="text-red-500">*</span></label>
              <input className="input w-full" value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))} required />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">อีเมล</label>
            <input type="email" className="input w-full" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} autoComplete="off" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">สิทธิ์การใช้งาน <span className="text-red-500">*</span></label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {PERMISSIONS.map(p => {
                const superuserOwn = p.value === 'manage_users' && user.is_superuser
                const notAllowed = p.value === 'manage_users' && !isSuperuser
                const locked = superuserOwn || notAllowed
                const hint = superuserOwn ? 'สิทธิ์ถาวรของ superuser'
                  : notAllowed ? 'เฉพาะ superuser เท่านั้น' : p.desc
                return (
                  <label key={p.value} className={`flex items-start gap-2.5 p-3 rounded-lg border transition-colors ${locked ? 'border-gray-100 bg-gray-50 cursor-not-allowed opacity-60' :
                      form.roles.includes(p.value) ? 'border-primary bg-primary/5 cursor-pointer' : 'border-gray-200 hover:border-gray-300 cursor-pointer'
                    }`}>
                    <input type="checkbox" className="mt-0.5 accent-primary shrink-0"
                      checked={form.roles.includes(p.value)} onChange={() => !locked && toggle(p.value)} disabled={locked} />
                    <div>
                      <div className="text-sm font-medium text-gray-800">{p.label}</div>
                      <div className="text-xs text-gray-400 leading-tight">{hint}</div>
                    </div>
                  </label>
                )
              })}
            </div>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
        <div className="flex gap-3 px-5 py-4 border-t border-gray-100 shrink-0">
          <button onClick={onClose} className="btn btn-ghost flex-1" disabled={loading}>ยกเลิก</button>
          <button onClick={handleSave} className="btn btn-primary flex-1" disabled={loading}>
            {loading ? 'กำลังบันทึก...' : 'บันทึก'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function UsersSettingsPage() {
  const router = useRouter()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)
  const [currentUserIsSuperuser, setCurrentUserIsSuperuser] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState<User | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [search, setSearch] = useState('')
  const [filterRoles, setFilterRoles] = useState<string[]>([])
  const [roleDropOpen, setRoleDropOpen] = useState(false)
  const roleDropRef = useRef<HTMLDivElement>(null)
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(25)

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    Promise.all([listUsers(), getMe()])
      .then(([us, me]) => {
        if (!me.is_superuser && !me.roles?.includes('manage_users')) { router.push(getHomeRoute(me)); return }
        setUsers(us)
        setCurrentUserId(me.user_id)
        setCurrentUserIsSuperuser(me.is_superuser)
      })
      .catch((err) => {
        // only redirect on auth failure — let interceptor handle 401, ignore other errors
        if (err?.response?.status === 403) router.push(getHomeRoute({ roles: [], is_superuser: false }))
      })
      .finally(() => setLoading(false))
  }, [router])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (roleDropRef.current && !roleDropRef.current.contains(e.target as Node)) setRoleDropOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleDelete = async () => {
    if (!confirmDelete) return
    setDeleting(true)
    try {
      await deleteUser(confirmDelete.user_id)
      setUsers(us => us.filter(u => u.user_id !== confirmDelete.user_id))
      setConfirmDelete(null)
    } catch {
      // ignore
    } finally {
      setDeleting(false)
    }
  }

  const filtered = users.filter(u => {
    const q = search.trim().toLowerCase()
    const matchName = !q || `${u.first_name} ${u.last_name} ${u.username}`.toLowerCase().includes(q)
    const matchRole = filterRoles.length === 0 || filterRoles.every(r => (u.roles ?? []).includes(r))
    return matchName && matchRole
  })

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-gray-400">กำลังโหลด...</div>
  )

  return (
    <div>
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-semibold text-gray-900">จัดการบัญชีผู้ใช้</h1>
          <button onClick={() => setShowAdd(true)} className="btn btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> เพิ่มผู้ใช้
          </button>
        </div>

        {/* Search + filter bar */}
        <div className="flex flex-col sm:flex-row gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              className="input w-full pl-9"
              placeholder="ค้นหาชื่อ หรือ username..."
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
            />
          </div>
          <div className="relative" ref={roleDropRef}>
            <button
              type="button"
              onClick={() => setRoleDropOpen(o => !o)}
              className={`input flex items-center justify-between gap-2 w-52 text-left ${filterRoles.length > 0 ? 'border-primary ring-2 ring-primary/20' : ''}`}
            >
              <span className={filterRoles.length > 0 ? 'text-gray-800' : 'text-gray-400'}>
                {filterRoles.length === 0 ? 'กรองตามสิทธิ์...' : `${filterRoles.length} สิทธิ์ที่เลือก`}
              </span>
              <svg className={`w-4 h-4 text-gray-400 shrink-0 transition-transform ${roleDropOpen ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" /></svg>
            </button>
            {roleDropOpen && (
              <div className="absolute left-0 top-full mt-1 w-56 bg-white rounded-xl border border-gray-100 shadow-lg py-1 z-30">
                {filterRoles.length > 0 && (
                  <button
                    type="button"
                    onClick={() => { setFilterRoles([]); setPage(1) }}
                    className="w-full text-left px-3 py-1.5 text-xs text-primary hover:bg-gray-50 font-medium"
                  >
                    ล้างทั้งหมด
                  </button>
                )}
                <div className={filterRoles.length > 0 ? 'border-t border-gray-50' : ''}>
                  {PERMISSIONS.map(p => {
                    const checked = filterRoles.includes(p.value)
                    return (
                      <label key={p.value} className="flex items-center gap-2.5 px-3 py-2 hover:bg-gray-50 cursor-pointer">
                        <input
                          type="checkbox"
                          className="accent-primary shrink-0"
                          checked={checked}
                          onChange={() => {
                            setFilterRoles(prev => checked ? prev.filter(r => r !== p.value) : [...prev, p.value])
                            setPage(1)
                          }}
                        />
                        <span className="text-sm text-gray-700">{p.label}</span>
                      </label>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">ชื่อ</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">ชื่อผู้ใช้</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">อีเมล</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filtered.slice((page - 1) * perPage, page * perPage).map(user => (
                <tr key={user.user_id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-800 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span>{user.first_name} {user.last_name}</span>
                      {user.is_superuser && (
                        <span className="shrink-0 text-xs font-semibold px-1.5 py-0.5 rounded bg-gray-800 text-white tracking-wide">ROOT</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500">{user.username}</td>
                  <td className="px-4 py-3 text-gray-500 hidden sm:table-cell">{user.email ?? <span className="text-gray-300">—</span>}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button onClick={() => setEditUser(user)} className="text-gray-300 hover:text-primary transition-colors" title="แก้ไขข้อมูล">
                        <Pencil className="w-4 h-4" />
                      </button>
                      {!user.is_superuser && user.user_id !== currentUserId && (
                        <button onClick={() => setConfirmDelete(user)} className="text-gray-300 hover:text-red-500 transition-colors" title="ลบบัญชี">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <p className="text-center text-gray-400 py-10">
              {users.length === 0 ? 'ไม่มีผู้ใช้ในระบบ' : 'ไม่พบผู้ใช้ที่ค้นหา'}
            </p>
          )}
          <Pagination page={page} perPage={perPage} total={filtered.length} onPageChange={setPage} onPerPageChange={(n) => { setPerPage(n); setPage(1) }} />
        </div>

      {showAdd && (
        <AddUserModal
          onClose={() => setShowAdd(false)}
          onCreated={user => { setUsers(us => [user, ...us]); setShowAdd(false) }}
          existingUsernames={users.map(u => u.username)}
          isSuperuser={currentUserIsSuperuser}
        />
      )}

      {editUser && (
        <EditUserModal
          user={editUser}
          onClose={() => setEditUser(null)}
          onUpdated={(updated: User) => { setUsers(us => us.map(u => u.user_id === updated.user_id ? updated : u)); setEditUser(null) }}
          isSuperuser={currentUserIsSuperuser}
        />
      )}

      {confirmDelete && (
        <DeleteConfirmModal
          user={confirmDelete}
          onCancel={() => setConfirmDelete(null)}
          onConfirm={handleDelete}
          loading={deleting}
        />
      )}
    </div>
  )
}
