'use client'

import { Suspense, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { Activity } from 'lucide-react'
import PasswordInput from '@/components/ui/PasswordInput'
import { resetPassword } from '@/lib/api'

function ResetPasswordForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token') ?? ''

  const [form, setForm] = useState({ new_password: '', confirm_password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  if (!token) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8 max-w-sm w-full text-center space-y-4">
        <p className="text-red-600">ลิงก์ไม่ถูกต้องหรือหมดอายุแล้ว</p>
        <Link href="/forgot-password" className="btn-primary w-full justify-center py-2.5 inline-flex">ขอลิงก์ใหม่</Link>
      </div>
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (form.new_password !== form.confirm_password) { setError('รหัสผ่านไม่ตรงกัน'); return }
    if (form.new_password.length < 6) { setError('รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร'); return }
    setLoading(true)
    try {
      await resetPassword(token, form.new_password)
      setDone(true)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'ลิงก์ไม่ถูกต้องหรือหมดอายุแล้ว กรุณาขอลิงก์ใหม่')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
      <div className="flex flex-col items-center mb-8">
        <div className="bg-primary rounded-xl p-3 mb-4">
          <Activity className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-xl font-semibold text-gray-800">ตั้งรหัสผ่านใหม่</h1>
      </div>

      {done ? (
        <div className="text-center space-y-4">
          <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto">
            <svg className="w-7 h-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-sm text-gray-600 font-medium">เปลี่ยนรหัสผ่านสำเร็จ</p>
          <p className="text-xs text-gray-400">คุณสามารถเข้าสู่ระบบด้วยรหัสผ่านใหม่ได้แล้ว</p>
          <button onClick={() => router.push('/login')} className="btn-primary w-full justify-center py-2.5">
            เข้าสู่ระบบ
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">รหัสผ่านใหม่</label>
            <PasswordInput className="input w-full" value={form.new_password}
              onChange={e => setForm(f => ({ ...f, new_password: e.target.value }))}
              required autoComplete="new-password" minLength={6} placeholder="อย่างน้อย 6 ตัวอักษร" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ยืนยันรหัสผ่านใหม่</label>
            <PasswordInput className="input w-full" value={form.confirm_password}
              onChange={e => setForm(f => ({ ...f, confirm_password: e.target.value }))}
              required autoComplete="new-password" />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" className="btn-primary w-full justify-center py-2.5" disabled={loading}>
            {loading ? 'กำลังบันทึก...' : 'บันทึกรหัสผ่านใหม่'}
          </button>
          <Link href="/forgot-password" className="block text-center text-xs text-gray-400 hover:text-gray-600 transition-colors">
            ขอลิงก์ใหม่
          </Link>
        </form>
      )}
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen bg-primary-bg flex items-center justify-center p-4">
      <Suspense fallback={<div className="bg-white rounded-2xl shadow-lg p-8 max-w-sm w-full text-center text-gray-400">กำลังโหลด...</div>}>
        <ResetPasswordForm />
      </Suspense>
    </div>
  )
}
