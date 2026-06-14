'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  AlertCircle,
  CheckCircle2,
  DatabaseZap,
  FileText,
  Loader2,
  Pencil,
  Plus,
  RefreshCw,
  Trash2,
  Upload,
} from 'lucide-react'
import Pagination from '@/components/ui/Pagination'
import Spinner from '@/components/ui/Spinner'
import {
  createTextDocument,
  deleteRagDocument,
  getIngestStatus,
  getTextDocument,
  listRagDocuments,
  renameRagDocument,
  triggerIngest,
  updateTextDocument,
  uploadRagDocument,
} from '@/lib/api'
import { isLoggedIn } from '@/lib/auth'
import { getHomeRoute } from '@/lib/routing'
import type { IngestStatus, RagDocument } from '@/lib/types'

function fileSize(bytes: number | null) {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function fmt(iso: string | null) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('th-TH', { dateStyle: 'short' })
}

type EditorModal =
  | { open: false }
  | { open: true; mode: 'create'; filename: string; content: string }
  | { open: true; mode: 'edit'; filename: string; storageKey: string; content: string }

export default function DocumentsPage() {
  const router = useRouter()
  const [docs, setDocs] = useState<RagDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<{ current: number; total: number; filename: string } | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [ingestStatus, setIngestStatus] = useState<IngestStatus | null>(null)
  const [ingesting, setIngesting] = useState(false)
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(25)
  const [editor, setEditor] = useState<EditorModal>({ open: false })
  const [saving, setSaving] = useState(false)
  const [editorLoading, setEditorLoading] = useState(false)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [deleting, setDeleting] = useState(false)
  const [renaming, setRenaming] = useState<{ key: string; value: string } | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const loadDocs = useCallback(async () => {
    setLoading(true)
    try {
      const data = await listRagDocuments()
      setDocs(data)
    } finally {
      setLoading(false)
    }
    setSelected(new Set())
  }, [])

  const loadStatus = useCallback(async () => {
    try {
      const s = await getIngestStatus()
      setIngestStatus(s)
    } catch {
      // silently ignore poll errors
    }
  }, [])

  useEffect(() => {
    if (!isLoggedIn()) { router.push('/login'); return }
    import('@/lib/api').then(({ getMe }) => getMe()).then(u => {
      if (!u.roles?.includes('manage_docs')) router.push(getHomeRoute(u))
      else {
        loadDocs()
        loadStatus()
      }
    }).catch(() => { if (!isLoggedIn()) router.push('/login') })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (ingestStatus?.status !== 'running') return
    const id = setInterval(async () => {
      const s = await getIngestStatus().catch(() => null)
      if (!s) return
      setIngestStatus(s)
      if (s.status !== 'running') {
        clearInterval(id)
        if (s.status === 'done') loadDocs()
      }
    }, 3000)
    return () => clearInterval(id)
  }, [ingestStatus?.status, loadStatus, loadDocs])

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    const fileArray = Array.from(files)
    setUploading(true)
    try {
      for (let i = 0; i < fileArray.length; i++) {
        const file = fileArray[i]
        setUploadProgress({ current: i + 1, total: fileArray.length, filename: file.name })
        await uploadRagDocument(file)
      }
      await loadDocs()
    } finally {
      setUploading(false)
      setUploadProgress(null)
    }
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    handleFiles(e.dataTransfer.files)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const remove = async (doc: { filename: string; storage_key: string }) => {
    if (!confirm(`ยืนยันการลบ "${doc.filename}"?`)) return
    await deleteRagDocument(doc.storage_key)
    setDocs(prev => prev.filter(d => d.storage_key !== doc.storage_key))
    setSelected(prev => { const n = new Set(prev); n.delete(doc.storage_key); return n })
  }

  const removeSelected = async () => {
    if (selected.size === 0) return
    const names = docs.filter(d => selected.has(d.storage_key)).map(d => d.filename)
    if (!confirm(`ยืนยันการลบ ${selected.size} ไฟล์?\n${names.slice(0, 5).join('\n')}${names.length > 5 ? `\n...และอีก ${names.length - 5} ไฟล์` : ''}`)) return
    setDeleting(true)
    try {
      await Promise.all([...selected].map(key => deleteRagDocument(key)))
      await loadDocs()
    } finally {
      setDeleting(false)
    }
  }

  const saveRename = async () => {
    if (!renaming || !renaming.value.trim()) { setRenaming(null); return }
    await renameRagDocument(renaming.key, renaming.value.trim())
    setDocs(prev => prev.map(d => d.storage_key === renaming.key ? { ...d, filename: renaming.value.trim() } : d))
    setRenaming(null)
  }

  const toggleOne = (key: string) => {
    setSelected(prev => {
      const n = new Set(prev)
      n.has(key) ? n.delete(key) : n.add(key)
      return n
    })
  }

  const handleIngest = async (mode: 'reingest' | 'append') => {
    if (mode === 'reingest') {
      if (!confirm('สร้างฐานข้อมูล AI ใหม่ทั้งหมด?\n\nAI จะลืมเอกสารเดิมทั้งหมด และเริ่มต้นใหม่จากศูนย์')) return
    }
    setIngesting(true)
    // Show running state immediately so polling kicks in without waiting for loadStatus()
    setIngestStatus({ status: 'running', mode, message: 'กำลังเริ่มต้น…', files_processed: 0, files_total: 0, updated_at: new Date().toISOString(), error: '' })
    try {
      await triggerIngest(mode)
    } catch {
      await loadStatus()
    } finally {
      setIngesting(false)
    }
  }

  const openCreate = () => setEditor({ open: true, mode: 'create', filename: '', content: '' })

  const openEdit = async (storageKey: string, displayName: string) => {
    setEditorLoading(true)
    setEditor({ open: true, mode: 'edit', filename: displayName, storageKey, content: '' })
    try {
      const data = await getTextDocument(storageKey)
      setEditor({ open: true, mode: 'edit', filename: displayName, storageKey, content: data.content })
    } finally {
      setEditorLoading(false)
    }
  }

  const saveEditor = async () => {
    if (!editor.open) return
    setSaving(true)
    try {
      if (editor.mode === 'create') {
        await createTextDocument(editor.filename, editor.content)
      } else {
        await updateTextDocument(editor.storageKey, editor.content)
      }
      setEditor({ open: false })
      await loadDocs()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="font-semibold text-gray-800">คลังเอกสารสำหรับ AI ตอบคำถาม</h2>
        <p className="text-xs text-gray-400">อัปโหลดเอกสารคำแนะนำหลังรักษา เพื่อให้ AI ใช้ตอบคำถามผู้ป่วย — หลังอัปโหลดให้กด "เปิดใช้งานเอกสารใหม่" เพื่อให้มีผล</p>
      </div>

      {/* Ingest action buttons */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        {selected.size > 0 && (
          <button
            type="button"
            onClick={removeSelected}
            disabled={deleting}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border border-red-300 bg-red-50 text-red-600 hover:bg-red-100 disabled:opacity-50 transition-colors"
          >
            {deleting ? <Spinner className="w-4 h-4" /> : <Trash2 className="w-4 h-4" />}
            ลบที่เลือก ({selected.size})
          </button>
        )}
        <button
          type="button"
          disabled={ingesting}
          onClick={() => handleIngest('append')}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          เปิดใช้งานเอกสารใหม่
        </button>
        <button
          type="button"
          disabled={ingesting}
          onClick={() => handleIngest('reingest')}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border border-red-300 bg-white text-red-600 hover:bg-red-50 disabled:opacity-50 transition-colors"
          title="ใช้เฉพาะเมื่อต้องการเริ่มต้นใหม่ทั้งหมด — AI จะลืมเอกสารเดิมทั้งหมด"
        >
          <DatabaseZap className="w-4 h-4" />
          สร้างฐานข้อมูล AI ใหม่ทั้งหมด
        </button>
      </div>

      {/* Ingest status bar */}
      {ingestStatus && ingestStatus.status !== 'idle' && (
        <div className={`rounded-lg px-4 py-3 mb-4 text-sm ${
          ingestStatus.status === 'running'
            ? 'bg-yellow-50 border border-yellow-200 text-yellow-800'
            : ingestStatus.status === 'done'
            ? 'bg-green-50 border border-green-200 text-green-800'
            : 'bg-red-50 border border-red-200 text-red-800'
        }`}>
          <div className="flex items-center gap-3">
            {ingestStatus.status === 'running' && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
            {ingestStatus.status === 'done' && <CheckCircle2 className="w-4 h-4 shrink-0" />}
            {ingestStatus.status === 'error' && <AlertCircle className="w-4 h-4 shrink-0" />}
            <span className="flex-1">
              {ingestStatus.status === 'error' ? ingestStatus.error || ingestStatus.message : ingestStatus.message}
            </span>
            {ingestStatus.status === 'running' && ingestStatus.files_total > 0 && (
              <span className="shrink-0 font-medium text-xs">
                {ingestStatus.files_processed}/{ingestStatus.files_total} ไฟล์
              </span>
            )}
          </div>
          {ingestStatus.status === 'running' && ingestStatus.files_total > 0 && (
            <div className="mt-2 bg-yellow-200 rounded-full h-1.5">
              <div
                className="bg-yellow-600 rounded-full h-1.5 transition-all duration-500"
                style={{ width: `${Math.round((ingestStatus.files_processed / ingestStatus.files_total) * 100)}%` }}
              />
            </div>
          )}
        </div>
      )}

      {/* Upload + Text editor side-by-side */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Drop zone */}
        <div
          className={`border-2 border-dashed rounded-xl p-5 sm:p-8 flex flex-col items-center gap-3 transition-colors cursor-pointer ${dragOver ? 'border-primary bg-primary-bg' : 'border-gray-300 bg-white hover:border-primary/50'}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
        >
          {uploading ? (
            <>
              <Spinner className="w-8 h-8" />
              <span className="text-sm text-gray-600 font-medium text-center">
                {uploadProgress
                  ? `กำลังอัปโหลด${uploadProgress.total > 1 ? ` (${uploadProgress.current}/${uploadProgress.total})` : ''}…`
                  : 'กำลังอัปโหลด…'}
              </span>
              {uploadProgress && (
                <span className="text-xs text-gray-400 max-w-[200px] truncate text-center">{uploadProgress.filename}</span>
              )}
              {uploadProgress && uploadProgress.total > 1 && (
                <div className="w-full max-w-[180px] bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-primary rounded-full h-1.5 transition-all duration-300"
                    style={{ width: `${(uploadProgress.current / uploadProgress.total) * 100}%` }}
                  />
                </div>
              )}
            </>
          ) : (
            <>
              <div className="bg-primary/10 rounded-full p-4">
                <Upload className="w-7 h-7 text-primary" />
              </div>
              <p className="text-gray-600 font-medium text-sm">อัปโหลดไฟล์ PDF / TXT</p>
              <p className="text-xs text-gray-400">ลากวางหรือคลิกเพื่อเลือกไฟล์</p>
              <button
                type="button"
                className="btn-primary text-sm"
                onClick={(e) => { e.stopPropagation(); fileRef.current?.click() }}
              >
                เลือกไฟล์จากเครื่อง
              </button>
            </>
          )}
          <input ref={fileRef} type="file" className="hidden" accept=".pdf,.txt,.md,.docx" multiple onChange={(e) => handleFiles(e.target.files)} />
        </div>

        {/* Text editor entry */}
        <div
          className="border-2 border-dashed border-gray-300 rounded-xl p-5 sm:p-8 flex flex-col items-center gap-3 bg-white hover:border-primary/50 transition-colors cursor-pointer"
          onClick={openCreate}
        >
          <div className="bg-blue-50 rounded-full p-4">
            <FileText className="w-7 h-7 text-blue-500" />
          </div>
          <p className="text-gray-600 font-medium text-sm">พิมพ์เนื้อหาโดยตรง</p>
          <p className="text-xs text-gray-400">สร้างเอกสารข้อความได้เลย ไม่ต้องอัปโหลดไฟล์</p>
          <button type="button" className="flex items-center gap-1.5 btn-outline text-sm" onClick={(e) => { e.stopPropagation(); openCreate() }}>
            <Plus className="w-4 h-4" />
            เพิ่มเนื้อหาใหม่
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden p-0">
        {loading ? (
          <div className="flex justify-center py-12"><Spinner className="w-8 h-8" /></div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-4 py-3 w-10">
                  {(() => {
                    const allKeys = docs.map(d => d.storage_key)
                    const allSel = allKeys.length > 0 && allKeys.every(k => selected.has(k))
                    const someSel = allKeys.some(k => selected.has(k))
                    return (
                      <input
                        type="checkbox"
                        checked={allSel}
                        ref={el => { if (el) el.indeterminate = someSel && !allSel }}
                        onChange={() => {
                          if (allSel) setSelected(new Set())
                          else setSelected(new Set(allKeys))
                        }}
                        className="rounded border-gray-300"
                        title="เลือกทั้งหมด"
                      />
                    )
                  })()}
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">#</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">ชื่อไฟล์</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">ขนาด</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">สถานะ</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">เปิดใช้งานล่าสุด</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {docs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-gray-400">ยังไม่มีเอกสาร</td>
                </tr>
              ) : (
                docs.slice((page - 1) * perPage, page * perPage).map((d, i) => (
                  <tr key={d.filename} className={`hover:bg-gray-50/50 ${selected.has(d.storage_key) ? 'bg-blue-50/50' : ''}`}>
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selected.has(d.storage_key)}
                        onChange={() => toggleOne(d.storage_key)}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="px-4 py-3 text-gray-400 hidden sm:table-cell">{(page - 1) * perPage + i + 1}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold px-1.5 py-0.5 rounded shrink-0 ${d.extension === '.pdf' ? 'bg-red-100 text-red-600' : d.extension === '.md' ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'}`}>
                          {d.extension.replace('.', '').toUpperCase() || 'FILE'}
                        </span>
                        {renaming?.key === d.storage_key ? (
                          <input
                            autoFocus
                            className="input py-0.5 px-2 text-sm h-7 max-w-[220px]"
                            value={renaming.value}
                            onChange={e => setRenaming(r => r ? { ...r, value: e.target.value } : r)}
                            onBlur={saveRename}
                            onKeyDown={e => { if (e.key === 'Enter') saveRename(); if (e.key === 'Escape') setRenaming(null) }}
                          />
                        ) : (
                          <span
                            className="text-gray-800 font-medium max-w-[160px] sm:max-w-[260px] truncate cursor-pointer hover:text-primary"
                            title="ดับเบิลคลิกเพื่อเปลี่ยนชื่อ"
                            onDoubleClick={() => setRenaming({ key: d.storage_key, value: d.filename })}
                          >
                            {d.filename}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-500 hidden sm:table-cell">{fileSize(d.size)}</td>
                    <td className="px-4 py-3">
                      {d.is_indexed ? (
                        <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-green-100 text-green-700">พร้อมใช้งาน</span>
                      ) : (
                        <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-500">ยังไม่เปิดใช้งาน</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-500 hidden md:table-cell">{fmt(d.last_ingested)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {(d.extension === '.txt' || d.extension === '.md') && (
                          <button
                            onClick={() => openEdit(d.storage_key, d.filename)}
                            className="text-gray-400 hover:text-primary transition-colors"
                            title="แก้ไขเนื้อหา"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => remove(d)}
                          className="text-gray-400 hover:text-red-500 transition-colors"
                          title="ลบเอกสาร"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
        <Pagination page={page} perPage={perPage} total={docs.length} onPageChange={setPage} onPerPageChange={(n) => { setPerPage(n); setPage(1) }} />
      </div>

      {/* Text editor modal */}
      {editor.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl flex flex-col max-h-[90vh]">
            <div className="px-4 sm:px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h2 className="font-semibold text-gray-800">
                {editor.mode === 'create' ? 'เพิ่มเนื้อหาใหม่' : `แก้ไข: ${editor.filename}`}
              </h2>
              <button onClick={() => setEditor({ open: false })} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
            </div>

            <div className="px-4 sm:px-6 py-4 flex flex-col gap-4 flex-1 overflow-hidden">
              {editor.mode === 'create' && (
                <div>
                  <label className="label">ชื่อเอกสาร <span className="text-red-500">*</span></label>
                  <div className="flex items-center gap-2">
                    <input
                      className="input flex-1"
                      placeholder="เช่น คำแนะนำหลังถอนฟัน"
                      value={editor.filename}
                      onChange={(e) => setEditor(prev => prev.open ? { ...prev, filename: e.target.value } : prev)}
                    />
                    <span className="text-sm text-gray-400 shrink-0">.txt</span>
                  </div>
                </div>
              )}
              <div className="flex flex-col flex-1 min-h-0">
                <label className="label mb-1">เนื้อหา</label>
                {editorLoading ? (
                  <div className="flex justify-center items-center flex-1"><Spinner className="w-6 h-6" /></div>
                ) : (
                  <textarea
                    className="input flex-1 resize-none font-mono text-sm leading-relaxed min-h-[320px]"
                    placeholder="พิมพ์เนื้อหาที่ต้องการให้ AI ใช้ตอบคำถามผู้ป่วย..."
                    value={editor.content}
                    onChange={(e) => setEditor(prev => prev.open ? { ...prev, content: e.target.value } : prev)}
                  />
                )}
              </div>
            </div>

            <div className="px-4 sm:px-6 py-4 border-t border-gray-100 flex gap-3 justify-end">
              <button onClick={() => setEditor({ open: false })} className="btn-outline">ยกเลิก</button>
              <button
                onClick={saveEditor}
                disabled={saving || editorLoading || (editor.mode === 'create' && !editor.filename.trim())}
                className="btn-primary flex items-center gap-2"
              >
                {saving && <Spinner className="w-3 h-3" />}
                บันทึก
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
