import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ระบบติดตามอาการผู้ป่วยหลังผ่าตัด',
  description: 'คณะทันตแพทยศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body>{children}</body>
    </html>
  )
}
