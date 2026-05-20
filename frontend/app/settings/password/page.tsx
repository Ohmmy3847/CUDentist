'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { KeyRound } from 'lucide-react'
import PasswordInput from '@/components/ui/PasswordInput'
import { confirmChangePassword, requestChangePassword } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'

export default function PasswordSettingsPage() {
  const router = useRouter()
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' })

  const [step, setStep] = useState<'form' | 'otp'>('form')
  const [otpSession, setOtpSession] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const otpRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
  }, [router])

  useEffect(() => {
    if (step === 'otp') setTimeout(() => otpRef.current?.focus(), 50)
  }, [step])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (form.new_password !== form.confirm_password) { setError('รหัสผ่านใหม่ไม่ตรงกัน'); return }
    if (form.new_password.length < 6) { setError('รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร'); return }
    setLoading(true)
    try {
      const result = await requestChangePassword(form.current_password, form.new_password)
      if (result.requires_otp && result.otp_session) {
        setOtpSession(result.otp_session)
        setStep('otp')
      } else {
        setSuccess(true)
        setForm({ current_password: '', new_password: '', confirm_password: '' })
      }
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setLoading(false)
    }
  }

  const handleOtp = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await confirmChangePassword(otpSession, otpCode)
      setSuccess(true)
      setStep('form')
      setForm({ current_password: '', new_password: '', confirm_password: '' })
      setOtpCode('')
      setOtpSession('')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่')
      setOtpCode('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <KeyRound className="w-5 h-5 text-primary" />
            </div>
            <h1 className="text-lg font-semibold text-gray-900">เปลี่ยนรหัสผ่าน</h1>
          </div>

          {step === 'form' ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">รหัสผ่านปัจจุบัน</label>
                <PasswordInput className="input w-full" value={form.current_password}
                  onChange={e => setForm(f => ({ ...f, current_password: e.target.value }))}
                  required autoComplete="current-password" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">รหัสผ่านใหม่</label>
                <PasswordInput className="input w-full" value={form.new_password}
                  onChange={e => setForm(f => ({ ...f, new_password: e.target.value }))}
                  required autoComplete="new-password" minLength={6} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ยืนยันรหัสผ่านใหม่</label>
                <PasswordInput className="input w-full" value={form.confirm_password}
                  onChange={e => setForm(f => ({ ...f, confirm_password: e.target.value }))}
                  required autoComplete="new-password" />
              </div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              {success && <p className="text-sm text-green-600">เปลี่ยนรหัสผ่านสำเร็จ</p>}
              <button type="submit" className="btn btn-primary w-full" disabled={loading}>
                {loading ? 'กำลังดำเนินการ...' : 'เปลี่ยนรหัสผ่าน'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleOtp} className="space-y-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-700 font-medium">ยืนยันตัวตนด้วย OTP</p>
                <p className="text-xs text-blue-500 mt-1">รหัส OTP ถูกส่งไปที่อีเมลของคุณแล้ว (มีอายุ 5 นาที)</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">รหัส OTP (6 หลัก)</label>
                <input ref={otpRef} className="input w-full text-center text-2xl tracking-[0.5em] font-mono"
                  value={otpCode} onChange={e => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  inputMode="numeric" autoComplete="one-time-code" maxLength={6} required />
              </div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              <button type="submit" className="btn btn-primary w-full" disabled={loading || otpCode.length < 6}>
                {loading ? 'กำลังยืนยัน...' : 'ยืนยัน OTP'}
              </button>
              <button type="button" onClick={() => { setStep('form'); setError(''); setOtpCode(''); setOtpSession('') }}
                className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors">
                ← กลับ
              </button>
            </form>
          )}
        </div>
    </div>
  )
}
