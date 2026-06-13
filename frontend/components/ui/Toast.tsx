'use client'

import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { CheckCircle, XCircle, X } from 'lucide-react'

type ToastType = 'success' | 'error'

interface ToastItem {
  id: number
  type: ToastType
  message: string
}

interface ToastContextValue {
  toast: (message: string, type?: ToastType) => void
  success: (message: string) => void
  error: (message: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

let _nextId = 0

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const timers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map())

  const dismiss = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id))
    clearTimeout(timers.current.get(id))
    timers.current.delete(id)
  }, [])

  const toast = useCallback((message: string, type: ToastType = 'success') => {
    const id = ++_nextId
    setToasts(prev => [...prev, { id, type, message }])
    const timer = setTimeout(() => dismiss(id), 4000)
    timers.current.set(id, timer)
  }, [dismiss])

  // clean up timers on unmount
  useEffect(() => () => { timers.current.forEach(clearTimeout) }, [])

  const value: ToastContextValue = {
    toast,
    success: (msg) => toast(msg, 'success'),
    error: (msg) => toast(msg, 'error'),
  }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none">
        {toasts.map(t => (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-start gap-3 rounded-xl px-4 py-3 shadow-lg border text-sm max-w-sm animate-slide-up
              ${t.type === 'success'
                ? 'bg-white border-green-200 text-gray-800'
                : 'bg-white border-red-200 text-gray-800'
              }`}
          >
            {t.type === 'success'
              ? <CheckCircle className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
              : <XCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            }
            <span className="flex-1 leading-snug">{t.message}</span>
            <button
              onClick={() => dismiss(t.id)}
              className="text-gray-400 hover:text-gray-600 shrink-0"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside ToastProvider')
  return ctx
}
