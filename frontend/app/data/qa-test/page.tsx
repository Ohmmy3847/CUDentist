'use client'

import { useRef, useState } from 'react'
import { Send, ChevronDown, ChevronUp, FileText, AlertCircle, CheckCircle, HelpCircle } from 'lucide-react'
import { askRag } from '@/lib/api'

interface QAResult {
  answer: string
  source: string
  used_chunks: { content: string; metadata: Record<string, string> }[]
}

interface HistoryItem {
  question: string
  result: QAResult
  ms: number
}

const SOURCE_LABEL: Record<string, { label: string; className: string }> = {
  rag:                   { label: 'RAG — ดึงจากเอกสาร',         className: 'bg-blue-50 text-blue-700 border-blue-200' },
  rule_based:            { label: 'Rule-based — จากบริบทผู้ป่วย', className: 'bg-green-50 text-green-700 border-green-200' },
  'Not enough information': { label: 'ไม่พบข้อมูลที่เกี่ยวข้อง',  className: 'bg-red-50 text-red-700 border-red-200' },
}

function SourceBadge({ source }: { source: string }) {
  const s = SOURCE_LABEL[source] ?? { label: source, className: 'bg-gray-100 text-gray-600 border-gray-200' }
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full border ${s.className}`}>
      {source === 'rag' && <FileText className="w-3 h-3" />}
      {source === 'rule_based' && <CheckCircle className="w-3 h-3" />}
      {source === 'Not enough information' && <AlertCircle className="w-3 h-3" />}
      {s.label}
    </span>
  )
}

function ChunkList({ chunks }: { chunks: QAResult['used_chunks'] }) {
  const [open, setOpen] = useState(false)
  if (!chunks.length) return null
  return (
    <div className="mt-3 border-t border-gray-100 pt-3">
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center gap-1 text-xs text-gray-400 hover:text-primary transition-colors"
      >
        {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        แหล่งข้อมูลที่ใช้ ({chunks.length} chunks)
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          {chunks.map((c, i) => (
            <div key={i} className="bg-gray-50 border border-gray-100 rounded-lg p-3">
              {c.metadata?.source && (
                <div className="text-xs text-primary font-medium mb-1 flex items-center gap-1">
                  <FileText className="w-3 h-3 shrink-0" />
                  {c.metadata.source}
                </div>
              )}
              <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-line">{c.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const EXAMPLE_QUESTIONS = [
  'ถอนฟันแล้วเลือดไม่หยุดทำยังไง?',
  'หลังผ่าตัดกินอาหารอะไรได้บ้าง?',
  'บวมหลังผ่าตัดปกติไหม ควรทำอย่างไร?',
  'ภาวะแทรกซ้อนของการผ่าฟันคุดมีอะไรบ้าง?',
]

export default function QATestPage() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const submit = async (q = question) => {
    const trimmed = q.trim()
    if (!trimmed || loading) return
    setLoading(true)
    setError(null)
    const t0 = Date.now()
    try {
      const result = await askRag(trimmed)
      setHistory(prev => [{ question: trimmed, result, ms: Date.now() - t0 }, ...prev])
      setQuestion('')
      textareaRef.current?.focus()
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'เกิดข้อผิดพลาด กรุณาลองใหม่')
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit()
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-base font-semibold text-gray-800">ทดสอบ AI ตอบคำถาม</h2>
        <p className="text-sm text-gray-500 mt-0.5">
          ทดสอบระบบ RAG โดยตรง — ไม่มีบริบทผู้ป่วย คำตอบดึงจากเอกสารใน ChromaDB ล้วนๆ
        </p>
      </div>

      {/* Input */}
      <div className="card space-y-3">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={handleKey}
          rows={3}
          placeholder="พิมพ์คำถาม เช่น ถอนฟันแล้วมีไข้ควรทำยังไง?"
          className="input resize-none"
          disabled={loading}
        />
        <div className="flex items-center justify-between gap-3">
          <div className="flex flex-wrap gap-1.5">
            {EXAMPLE_QUESTIONS.map(q => (
              <button
                key={q}
                onClick={() => { setQuestion(q); submit(q) }}
                disabled={loading}
                className="text-xs px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-primary/10 hover:text-primary transition-colors disabled:opacity-40"
              >
                {q}
              </button>
            ))}
          </div>
          <button
            onClick={() => submit()}
            disabled={!question.trim() || loading}
            className="btn-primary flex items-center gap-2 shrink-0 disabled:opacity-50"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                กำลังประมวลผล...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                ถาม (⌘↵)
              </>
            )}
          </button>
        </div>
        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {history.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center py-16 text-gray-400 gap-2">
          <HelpCircle className="w-10 h-10 text-gray-300" />
          <p className="text-sm">ยังไม่มีคำถาม — ลองพิมพ์หรือคลิกตัวอย่าง</p>
        </div>
      )}

      {history.map((item, i) => (
        <div key={i} className="card space-y-3">
          {/* Question */}
          <div className="flex items-start gap-2">
            <span className="text-xs font-semibold text-gray-400 shrink-0 mt-0.5">Q</span>
            <p className="text-sm font-medium text-gray-800">{item.question}</p>
          </div>

          {/* Meta */}
          <div className="flex items-center gap-2 flex-wrap">
            <SourceBadge source={item.result.source} />
            <span className="text-xs text-gray-400">{(item.ms / 1000).toFixed(1)}s</span>
          </div>

          {/* Answer */}
          <div className="bg-gray-50 rounded-lg px-4 py-3 border-l-4 border-l-primary/40">
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
              {item.result.answer}
            </p>
          </div>

          <ChunkList chunks={item.result.used_chunks} />
        </div>
      ))}
    </div>
  )
}
