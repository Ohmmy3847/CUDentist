import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ระบบประเมินความเสี่ยงผู้ป่วยหลังผ่าตัด',
  description: 'Risk Assessment System for Post-Operative Patients',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="th">
      <body>{children}</body>
    </html>
  )
}
