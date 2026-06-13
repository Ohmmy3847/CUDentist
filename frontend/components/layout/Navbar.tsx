'use client'

import Link from 'next/link'
import { useEffect, useRef, useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { Activity, ChevronDown, Database, History, LogOut, Settings } from 'lucide-react'
import { clearToken } from '@/lib/auth'
import { getMe } from '@/lib/api'
import type { User } from '@/lib/types'

const PERM_LABEL: Record<string, string> = {
  send_assessment: 'ส่งแบบประเมิน',
  view_cases: 'ดูเคสที่รับผิดชอบ',
  view_all_cases: 'ดูเคสทั้งหมด',
  add_case: 'เพิ่มเคส',
  edit_case: 'แก้ไขเคส',
  manage_users: 'จัดการบัญชี',
  manage_docs: 'จัดการเอกสาร',
}

export default function Navbar() {
  const pathname = usePathname()
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    getMe().then(setUser).catch(() => {})
  }, [])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const logout = () => {
    clearToken()
    router.push('/login')
  }

  const has = (p: string) => user?.roles?.includes(p) ?? false

  const NAV = [
    ...(has('view_cases') || has('view_all_cases') ? [
      { href: '/dashboard', label: 'Dashboard', icon: Activity },
      { href: '/history', label: 'ประวัติย้อนหลัง', icon: History },
    ] : []),
    ...(has('manage_docs') ? [
      { href: '/data', label: 'ข้อมูล/เอกสาร', icon: Database },
    ] : []),
  ]

  return (
    <header className="bg-primary text-white shadow-md">
      <div className="max-w-screen-xl mx-auto flex items-center gap-6 px-4 h-14">
        {/* Brand */}
        <Link href="/dashboard" className="flex items-center gap-2 shrink-0">
          <Activity className="w-5 h-5" strokeWidth={2.5} />
          <div className="hidden sm:block leading-tight">
            <div className="text-sm font-semibold">ระบบติดตามอาการผู้ป่วยหลังผ่าตัด</div>
            <div className="text-[10px] opacity-70">คณะทันตแพทยศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย</div>
          </div>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-1 flex-1">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(href + '/')
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors whitespace-nowrap ${
                  active ? 'bg-white/20' : 'hover:bg-white/10'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="hidden md:block">{label}</span>
              </Link>
            )
          })}
        </nav>

        {/* User dropdown */}
        <div className="relative shrink-0" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(o => !o)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-sm hover:bg-white/10 transition-colors"
          >
            <span className="hidden sm:block max-w-[140px] truncate">
              {user ? `${user.first_name} ${user.last_name}` : '...'}
            </span>
            <ChevronDown className={`w-4 h-4 transition-transform ${menuOpen ? 'rotate-180' : ''}`} />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-1 w-48 max-w-[calc(100vw-1rem)] bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50 text-gray-700">
              {user && (
                <div className="px-3 py-2 border-b border-gray-100">
                  <div className="text-xs font-semibold text-gray-800 truncate">{`${user.first_name} ${user.last_name}`}</div>
                  <div className="text-[11px] text-gray-400">{(user.roles ?? []).map(r => PERM_LABEL[r] ?? r).join(', ')}</div>
                </div>
              )}
              <Link
                href="/settings/account"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
              >
                <Settings className="w-4 h-4 text-gray-400" />
                ตั้งค่า
              </Link>
              <button
                onClick={logout}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 transition-colors text-red-600"
              >
                <LogOut className="w-4 h-4" />
                ออกจากระบบ
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
