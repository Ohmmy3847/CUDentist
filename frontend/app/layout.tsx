'use client';

import type { Metadata } from 'next'
import './globals.css'
import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { th, en } from '@/lib/locales'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [lang, setLang] = useState<'th' | 'en'>('th');
  const pathname = usePathname();
  const t = lang === 'th' ? th : en;

  // Hide language switcher in form and result pages
  const hideLanguageSwitcher = pathname?.includes('/form') || pathname?.includes('/result');

  useEffect(() => {
    // Broadcast language change to other components
    window.dispatchEvent(new CustomEvent('languageChange', { detail: lang }));
  }, [lang]);

  const toggleLanguage = () => {
    setLang(prev => prev === 'th' ? 'en' : 'th');
  };

  return (
    <html lang={lang}>
      <head>
        <title>ระบบประเมินความเสี่ยงผู้ป่วยหลังผ่าตัด</title>
        <meta name="description" content="Risk Assessment System for Post-Operative Patients" />
      </head>
      <body className="font-cu bg-cu-gray min-h-screen">
        <header className="cu-header">
          <div className="container mx-auto px-1 md:px-1 flex items-center justify-between h-full">
            <div className="flex-1 min-w-0 pr-2">
              <div className="text-lg md:text-2xl font-bold leading-tight">
                {lang === 'th' ? 'ระบบประเมินความเสี่ยงผู้ป่วยหลังผ่าตัด' : 'Post-Operative Patient Risk Assessment System'}
              </div>
              <div className="text-xs md:text-base font-normal mt-1 leading-tight">
                {lang === 'th' ? 'คณะทันตแพทยศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย' : 'Faculty of Dentistry, Chulalongkorn University'}
              </div>
            </div>
            {!hideLanguageSwitcher && (
              <button
                onClick={toggleLanguage}
                className="flex-shrink-0 flex items-center justify-center w-14 h-9 bg-white/10 hover:bg-white/20 rounded-lg transition-all text-white font-bold border border-white/30 hover:border-white/50"
                style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}
              >
                <span className="w-full text-center">{lang === 'th' ? 'EN' : 'TH'}</span>
              </button>
            )}
          </div>
        </header>
        <main className="flex flex-col items-center justify-center w-full">
          {children}
        </main>
      </body>
    </html>
  )
}
