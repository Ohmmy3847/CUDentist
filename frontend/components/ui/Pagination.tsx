import { ChevronLeft, ChevronRight } from 'lucide-react'

interface Props {
  page: number
  perPage: number
  total: number
  onPageChange: (p: number) => void
  onPerPageChange: (n: number) => void
}

const PER_PAGE_OPTS = [10, 25, 50, 100]

export default function Pagination({ page, perPage, total, onPageChange, onPerPageChange }: Props) {
  const totalPages = Math.max(1, Math.ceil(total / perPage))
  const from = total === 0 ? 0 : (page - 1) * perPage + 1
  const to = Math.min(page * perPage, total)

  const pages: (number | '...')[] = []
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) pages.push(i)
  } else {
    pages.push(1)
    if (page > 3) pages.push('...')
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) pages.push(i)
    if (page < totalPages - 2) pages.push('...')
    pages.push(totalPages)
  }

  return (
    <div className="flex items-center justify-between px-4 py-2.5 border-t border-gray-100 text-sm">
      <div className="flex items-center gap-2 text-gray-500">
        <span>แสดง</span>
        <select
          className="border border-gray-200 rounded-md px-2 py-1 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-primary"
          value={perPage}
          onChange={(e) => { onPerPageChange(Number(e.target.value)); onPageChange(1) }}
        >
          {PER_PAGE_OPTS.map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
        <span>รายการ</span>
        <span className="text-gray-400 ml-2">{from}–{to} จาก {total} รายการ</span>
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        {pages.map((p, i) =>
          p === '...' ? (
            <span key={`dots-${i}`} className="px-2 text-gray-400">…</span>
          ) : (
            <button
              key={p}
              onClick={() => onPageChange(p)}
              className={`min-w-[32px] h-8 rounded-md text-sm font-medium transition-colors ${
                p === page ? 'bg-primary text-white' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {p}
            </button>
          )
        )}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
