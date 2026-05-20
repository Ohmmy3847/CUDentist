interface Props {
  risk: string | null | undefined
  size?: 'sm' | 'md'
}

const RISK_MAP: Record<string, { label: string; cls: string }> = {
  'ความเสี่ยงสูง': { label: 'เสี่ยงสูง', cls: 'bg-red-100 text-red-700 border border-red-300' },
  'ความเสี่ยงกลาง': { label: 'เสี่ยงกลาง', cls: 'bg-yellow-100 text-yellow-700 border border-yellow-300' },
  'ความเสี่ยงต่ำ': { label: 'เสี่ยงต่ำ', cls: 'bg-green-100 text-green-700 border border-green-300' },
  'High Risk': { label: 'High Risk', cls: 'bg-red-100 text-red-700 border border-red-300' },
  'Medium Risk': { label: 'Medium Risk', cls: 'bg-yellow-100 text-yellow-700 border border-yellow-300' },
  'Low Risk': { label: 'Low Risk', cls: 'bg-green-100 text-green-700 border border-green-300' },
  'Complicated': { label: 'Complicated', cls: 'bg-orange-100 text-orange-700 border border-orange-300' },
  low: { label: 'เสี่ยงต่ำ', cls: 'bg-green-100 text-green-700 border border-green-300' },
  medium: { label: 'เสี่ยงกลาง', cls: 'bg-yellow-100 text-yellow-700 border border-yellow-300' },
  high: { label: 'เสี่ยงสูง', cls: 'bg-red-100 text-red-700 border border-red-300' },
  complex: { label: 'ซับซ้อน', cls: 'bg-orange-100 text-orange-700 border border-orange-300' },
}

export default function RiskBadge({ risk, size = 'sm' }: Props) {
  const mapped = risk ? RISK_MAP[risk] : null
  const label = mapped?.label ?? (risk || 'ยังไม่เริ่ม')
  const cls = mapped?.cls ?? 'bg-gray-100 text-gray-500 border border-gray-200'
  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
  return <span className={`inline-flex items-center rounded-full font-medium ${padding} ${cls}`}>{label}</span>
}
