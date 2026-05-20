'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import Navbar from '@/components/layout/Navbar'

const SIDEBAR = [
  { href: '/data/symptoms', label: 'ข้อมูลอาการอื่น ๆ (เพิ่มเติม)' },
  { href: '/data/documents', label: 'คลังเอกสารสำหรับตอบคำถาม' },
]

export default function DataLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-screen-xl mx-auto px-4 py-6">
        <h1 className="text-xl font-semibold text-gray-800 mb-4">หัวข้อคลังข้อมูล/เอกสาร</h1>
        <div className="flex gap-6">
          {/* Sidebar */}
          <aside className="w-56 shrink-0">
            <div className="card p-2 space-y-1">
              {SIDEBAR.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`block px-3 py-2 rounded-lg text-sm transition-colors ${
                    pathname === item.href
                      ? 'bg-primary text-white font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </aside>
          {/* Main */}
          <div className="flex-1 min-w-0">{children}</div>
        </div>
      </div>
    </div>
  )
}
