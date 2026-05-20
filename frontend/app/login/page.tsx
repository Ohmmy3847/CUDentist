'use client'

import { useEffect, useRef, useState } from 'react'
import { Activity } from 'lucide-react'
import Link from 'next/link'
import { getMe, login, verifyOtp } from '@/lib/api'
import { getToken, saveToken } from '@/lib/auth'
import { getHomeRoute } from '@/lib/routing'
import PasswordInput from '@/components/ui/PasswordInput'

const DEVICE_TOKEN_KEY = 'device_token'

function getStoredDeviceToken() {
  if (typeof window === 'undefined') return undefined
  return localStorage.getItem(DEVICE_TOKEN_KEY) ?? undefined
}

function saveDeviceToken(token: string) {
  localStorage.setItem(DEVICE_TOKEN_KEY, token)
}

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(true)

  // OTP step
  const [step, setStep] = useState<'credentials' | 'otp'>('credentials')
  const [otpSession, setOtpSession] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [rememberDevice, setRememberDevice] = useState(false)
  const otpInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!getToken()) { setChecking(false); return }
    getMe()
      .then((me) => { window.location.replace(getHomeRoute(me)) })
      .catch(() => { setChecking(false) })
  }, [])

  useEffect(() => {
    if (step === 'otp') setTimeout(() => otpInputRef.current?.focus(), 50)
  }, [step])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = await login(username, password, getStoredDeviceToken())
      if (result.requires_2fa && result.otp_session) {
        setOtpSession(result.otp_session)
        setStep('otp')
        setLoading(false)
        return
      }
      if (result.access_token) {
        saveToken(result.access_token)
        const me = await getMe()
        window.location.replace(getHomeRoute(me))
      }
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('ไม่พบชื่อผู้ใช้นี้ในระบบ')
      } else if (err.response?.status === 401) {
        setError('รหัสผ่านไม่ถูกต้อง')
      } else if (err.response?.status === 403) {
        setError('บัญชีนี้ถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ')
      } else {
        setError('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์')
      }
      setLoading(false)
    }
  }

  const submitOtp = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = await verifyOtp(otpSession, otpCode, rememberDevice)
      if (result.device_token) saveDeviceToken(result.device_token)
      saveToken(result.access_token)
      const me = await getMe()
      window.location.replace(getHomeRoute(me))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่')
      setOtpCode('')
      setLoading(false)
    }
  }

  if (checking) return null

  return (
    <div className="min-h-screen bg-primary-bg flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-primary rounded-xl p-3 mb-4">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-gray-800 text-center">ระบบติดตามอาการผู้ป่วยหลังผ่าตัด</h1>
          <p className="text-sm text-gray-500 text-center mt-1">คณะทันตแพทยศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย</p>
        </div>

        {step === 'credentials' ? (
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">ชื่อผู้ใช้ หรือ อีเมล</label>
              <input className="input" value={username} onChange={(e) => setUsername(e.target.value)}
                autoComplete="username email" required />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="label !mb-0">รหัสผ่าน</label>
                <Link href="/forgot-password" className="text-xs text-primary hover:underline">ลืมรหัสผ่าน?</Link>
              </div>
              <PasswordInput className="input w-full" value={password}
                onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
              {loading ? 'กำลังตรวจสอบ...' : 'เข้าสู่ระบบ'}
            </button>
          </form>
        ) : (
          <form onSubmit={submitOtp} className="space-y-4">
            <div className="text-center mb-2">
              <p className="text-sm text-gray-600">รหัส OTP ถูกส่งไปที่อีเมลของคุณแล้ว</p>
              <p className="text-xs text-gray-400 mt-1">มีอายุ 5 นาที</p>
            </div>
            <div>
              <label className="label">รหัส OTP (6 หลัก)</label>
              <input ref={otpInputRef}
                className="input text-center text-2xl tracking-[0.5em] font-mono"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                inputMode="numeric" autoComplete="one-time-code" maxLength={6} required />
            </div>
            <label className="flex items-center gap-2.5 cursor-pointer select-none">
              <input type="checkbox" className="w-4 h-4 accent-primary rounded"
                checked={rememberDevice} onChange={e => setRememberDevice(e.target.checked)} />
              <span className="text-sm text-gray-600">จำอุปกรณ์นี้ไว้ 30 วัน</span>
            </label>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button type="submit" disabled={loading || otpCode.length < 6}
              className="btn-primary w-full justify-center py-2.5">
              {loading ? 'กำลังยืนยัน...' : 'ยืนยัน OTP'}
            </button>
            <button type="button"
              onClick={() => { setStep('credentials'); setError(''); setOtpCode(''); setOtpSession('') }}
              className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors">
              ← กลับไปหน้าเข้าสู่ระบบ
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
