'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { FileText } from 'lucide-react';
import { th, en } from '@/lib/locales';

export default function Home() {
  const [lang, setLang] = useState<'th' | 'en'>('th');
  const t = lang === 'th' ? th.home : en.home;

  useEffect(() => {
    const handleLanguageChange = (e: CustomEvent) => {
      setLang(e.detail);
    };
    window.addEventListener('languageChange', handleLanguageChange as EventListener);
    return () => window.removeEventListener('languageChange', handleLanguageChange as EventListener);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 w-full">
      <div className="container mx-auto px-4 py-16">
        {/* Options */}
        <div className="max-w-2xl mx-auto">
          {/* Form Option */}
          <Link href={`/form?lang=${lang}`}>
            <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 cursor-pointer border-2 border-transparent hover:border-cu-pink-500 group">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="p-6 bg-pink-100 rounded-full group-hover:bg-cu-pink-500 transition-colors duration-300">
                  <FileText className="w-16 h-16 text-cu-pink-600 group-hover:text-white transition-colors duration-300" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800">{t.startForm.title}</h2>
                <p className="text-gray-600">
                  {t.startForm.description}
                </p>
                <div className="pt-4">
                  <span className="inline-block px-6 py-3 bg-pink-600 text-white rounded-lg group-hover:bg-pink-700 transition-colors duration-300">
                    {t.startForm.button}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        </div>
        
        {/* Info Section */}
        <div className="max-w-3xl mx-auto mt-16 bg-white rounded-xl shadow-md p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">{t.info.title}</h3>
          <ul className="space-y-3 text-gray-700">
            {t.info.list.map((item, index) => (
              <li key={index} className="flex items-start">
                <span className="text-cu-pink-600 mr-2">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  );
}
