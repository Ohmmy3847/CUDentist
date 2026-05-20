'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { KeyRound, Settings, User as UserIcon, Users } from 'lucide-react'
import Navbar from '@/components/layout/Navbar'
import { getMe } from '@/lib/api'

const NAV_ITEMS = [
  { href: '/settings/account', label: 'ข้อมูลส่วนตัว', icon: UserIcon },
  { href: '/settings/password', label: 'เปลี่ยนรหัสผ่าน', icon: KeyRound },
]

const ADMIN_ITEMS = [
  { href: '/settings/users', label: 'จัดการบัญชีผู้ใช้', icon: Users },
]

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [canManageUsers, setCanManageUsers] = useState(false)

  useEffect(() => {
    getMe().then(u => {
      setCanManageUsers(!!(u.is_superuser || u.roles?.includes('manage_users')))
    }).catch(() => {})
  }, [])

  const allItems = canManageUsers ? [...NAV_ITEMS, ...ADMIN_ITEMS] : NAV_ITEMS

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-screen-lg mx-auto px-4 py-8">
        <div className="flex items-center gap-2 mb-6">
          <Settings className="w-5 h-5 text-gray-500" />
          <h1 className="text-lg font-semibold text-gray-800">ตั้งค่า</h1>
        </div>

        <div className="flex gap-6 items-start">
          {/* Sidebar */}
          <aside className="w-52 shrink-0">
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
              {allItems.map((item) => {
                const Icon = item.icon
                const active = pathname === item.href
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 py-3 text-sm font-medium transition-colors border-b border-gray-50 last:border-0 ${
                      active
                        ? 'pl-[14px] pr-4 bg-primary/5 text-primary border-l-[3px] border-l-primary'
                        : 'px-4 text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    {item.label}
                  </Link>
                )
              })}
            </div>
          </aside>

          {/* Content */}
          <main className="flex-1 min-w-0">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}
