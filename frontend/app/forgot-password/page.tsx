'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Activity, ArrowLeft } from 'lucide-react'
import { forgotPassword } from '@/lib/api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await forgotPassword(email)
      setSent(true)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('ไม่พบบัญชีที่ผูกกับอีเมลนี้ กรุณาตรวจสอบอีเมลอีกครั้ง')
      } else {
        setError('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-primary-bg flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-primary rounded-xl p-3 mb-4">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-gray-800">ลืมรหัสผ่าน</h1>
          <p className="text-sm text-gray-500 text-center mt-1">กรอกอีเมลที่ผูกกับบัญชีของคุณ</p>
        </div>

        {sent ? (
          <div className="text-center space-y-4">
            <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto">
              <svg className="w-7 h-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-sm text-gray-600">หากอีเมล <strong>{email}</strong> มีในระบบ คุณจะได้รับลิงก์รีเซ็ตรหัสผ่านในไม่ช้า</p>
            <p className="text-xs text-gray-400">ลิงก์มีอายุ 1 ชั่วโมง กรุณาตรวจสอบกล่อง Spam ด้วย</p>
            <Link href="/login" className="btn-primary w-full justify-center py-2.5 inline-flex">
              กลับหน้าเข้าสู่ระบบ
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">อีเมล</label>
              <input type="email" className="input w-full" value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="email" required placeholder="example@email.com" />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
              {loading ? 'กำลังส่ง...' : 'ส่งลิงก์รีเซ็ตรหัสผ่าน'}
            </button>
            <Link href="/login" className="flex items-center justify-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition-colors">
              <ArrowLeft className="w-4 h-4" /> กลับหน้าเข้าสู่ระบบ
            </Link>
          </form>
        )}
      </div>
    </div>
  )
}
