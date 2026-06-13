import type { Metadata } from 'next'
import './globals.css'
import { ToastProvider } from '@/components/ui/Toast'

export const metadata: Metadata = {
  title: 'ระบบติดตามอาการผู้ป่วยหลังผ่าตัด',
  description: 'คณะทันตแพทยศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body><ToastProvider>{children}</ToastProvider></body>
    </html>
  )
}
