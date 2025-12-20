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
      <body className="font-cu bg-cu-gray min-h-screen">
        <header className="cu-header">
          ระบบประเมินความเสี่ยงผู้ป่วยหลังผ่าตัด<br />
          <span style={{fontSize:'1.1rem',fontWeight:400}}>คณะทันตแพทยศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย</span>
        </header>
        <main className="flex flex-col items-center justify-center w-full">
          {children}
        </main>
      </body>
    </html>
  )
}
