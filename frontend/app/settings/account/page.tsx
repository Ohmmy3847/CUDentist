'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Mail, User as UserIcon } from 'lucide-react'
import { confirmChangeEmail, getMe, requestChangeEmail, updateMe } from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import type { User } from '@/lib/types'

export default function AccountSettingsPage() {
  const router = useRouter()
  const [me, setMe] = useState<User | null>(null)
  const [form, setForm] = useState({ first_name: '', last_name: '', username: '' })
  const [profileLoading, setProfileLoading] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [profileSuccess, setProfileSuccess] = useState(false)

  // Email change flow
  const [currentEmail, setCurrentEmail] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [emailStep, setEmailStep] = useState<'form' | 'otp'>('form')
  const [emailOtpSession, setEmailOtpSession] = useState('')
  const [emailOtpCode, setEmailOtpCode] = useState('')
  const [emailLoading, setEmailLoading] = useState(false)
  const [emailError, setEmailError] = useState('')
  const [emailSuccess, setEmailSuccess] = useState(false)
  const emailOtpRef = useRef<HTMLInputElement>(null)

  const isAdmin = me?.is_superuser || me?.roles?.includes('manage_users')

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    getMe().then(u => {
      setMe(u)
      setForm({ first_name: u.first_name || '', last_name: u.last_name || '', username: u.username || '' })
      setCurrentEmail(u.email || '')
      setNewEmail(u.email || '')
    }).catch(() => {})
  }, [router])

  useEffect(() => {
    if (emailStep === 'otp') setTimeout(() => emailOtpRef.current?.focus(), 50)
  }, [emailStep])

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileError('')
    setProfileSuccess(false)
    setProfileLoading(true)
    try {
      const payload: Parameters<typeof updateMe>[0] = { username: form.username }
      if (isAdmin) {
        payload.first_name = form.first_name
        payload.last_name = form.last_name
      }
      const updated = await updateMe(payload)
      setMe(updated)
      setForm({ first_name: updated.first_name || '', last_name: updated.last_name || '', username: updated.username || '' })
      setProfileSuccess(true)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setProfileError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setProfileLoading(false)
    }
  }

  const handleEmailRequest = async (e: React.FormEvent) => {
    e.preventDefault()
    setEmailError('')
    setEmailSuccess(false)
    if (newEmail === currentEmail) { setEmailError('อีเมลนี้เหมือนกับอีเมลปัจจุบัน'); return }
    setEmailLoading(true)
    try {
      const result = await requestChangeEmail(newEmail)
      setEmailOtpSession(result.otp_session)
      setEmailStep('otp')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setEmailError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setEmailLoading(false)
    }
  }

  const handleEmailConfirm = async (e: React.FormEvent) => {
    e.preventDefault()
    setEmailError('')
    setEmailLoading(true)
    try {
      await confirmChangeEmail(emailOtpSession, emailOtpCode)
      setCurrentEmail(newEmail)
      setEmailSuccess(true)
      setEmailStep('form')
      setEmailOtpCode('')
      setEmailOtpSession('')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setEmailError(msg || 'รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่')
      setEmailOtpCode('')
    } finally {
      setEmailLoading(false)
    }
  }

  return (
    <div className="max-w-lg space-y-6">

        {/* Profile card */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <UserIcon className="w-5 h-5 text-primary" />
            </div>
            <h1 className="text-lg font-semibold text-gray-900">ข้อมูลส่วนตัว</h1>
          </div>

          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ชื่อ</label>
                <input type="text" className="input w-full disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                  value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))}
                  disabled={!isAdmin} required={!!isAdmin} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">นามสกุล</label>
                <input type="text" className="input w-full disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                  value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))}
                  disabled={!isAdmin} required={!!isAdmin} />
              </div>
            </div>
            {!isAdmin && <p className="text-xs text-gray-400 -mt-2">ชื่อ-นามสกุลแก้ไขได้เฉพาะผู้ดูแลระบบ</p>}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ชื่อผู้ใช้ (Username)</label>
              <input type="text" className="input w-full" value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                autoComplete="username" required />
            </div>

            {profileError && <p className="text-sm text-red-600">{profileError}</p>}
            {profileSuccess && <p className="text-sm text-green-600">บันทึกข้อมูลสำเร็จ</p>}

            <button type="submit" className="btn btn-primary w-full" disabled={profileLoading}>
              {profileLoading ? 'กำลังบันทึก...' : 'บันทึกข้อมูล'}
            </button>
          </form>
        </div>

        {/* Email card */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <Mail className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">อีเมล</h2>
              <p className="text-xs text-gray-400">ใช้สำหรับรับ OTP และการแจ้งเตือน</p>
            </div>
          </div>

          {emailStep === 'form' ? (
            <form onSubmit={handleEmailRequest} className="space-y-4">
              {currentEmail && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">อีเมลปัจจุบัน</label>
                  <p className="text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">{currentEmail}</p>
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {currentEmail ? 'อีเมลใหม่' : 'อีเมล'}
                </label>
                <input type="email" className="input w-full" value={newEmail}
                  onChange={e => setNewEmail(e.target.value)}
                  autoComplete="email" required placeholder="example@email.com" />
              </div>
              {emailError && <p className="text-sm text-red-600">{emailError}</p>}
              {emailSuccess && <p className="text-sm text-green-600">เปลี่ยนอีเมลสำเร็จ</p>}
              {!emailError && !emailSuccess && newEmail === currentEmail && newEmail && (
                <p className="text-xs text-gray-400">กรอกอีเมลใหม่ที่ต้องการเปลี่ยน</p>
              )}
              <button type="submit" className="btn btn-primary w-full" disabled={emailLoading || newEmail === currentEmail}>
                {emailLoading ? 'กำลังส่ง OTP...' : 'ยืนยันเปลี่ยนอีเมล'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleEmailConfirm} className="space-y-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-700 font-medium">ยืนยันอีเมลใหม่ด้วย OTP</p>
                <p className="text-xs text-blue-500 mt-1">ส่งรหัสไปที่ <strong>{newEmail}</strong> แล้ว (มีอายุ 5 นาที)</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">รหัส OTP (6 หลัก)</label>
                <input ref={emailOtpRef} className="input w-full text-center text-2xl tracking-[0.5em] font-mono"
                  value={emailOtpCode} onChange={e => setEmailOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  inputMode="numeric" autoComplete="one-time-code" maxLength={6} required />
              </div>
              {emailError && <p className="text-sm text-red-600">{emailError}</p>}
              <button type="submit" className="btn btn-primary w-full" disabled={emailLoading || emailOtpCode.length < 6}>
                {emailLoading ? 'กำลังยืนยัน...' : 'ยืนยัน OTP'}
              </button>
              <button type="button" onClick={() => { setEmailStep('form'); setEmailError(''); setEmailOtpCode(''); setEmailOtpSession('') }}
                className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors">
                ← กลับ
              </button>
            </form>
          )}
        </div>

    </div>
  )
}
