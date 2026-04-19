import { Zap, Tag, Palette, Clock } from 'lucide-react'
import type { QueryAnalysis } from '../types'

interface Props {
  analysis: QueryAnalysis
  latencyMs?: number
  total: number
  algorithm: string
}

export default function QueryInsights({ analysis, latencyMs, total, algorithm }: Props) {
  const chips = [
    ...(analysis.genres || []).map(g => ({ label: g, icon: <Tag size={11} />, color: '#5a9ae0' })),
    ...(analysis.themes || []).map(t => ({ label: t, icon: <Palette size={11} />, color: '#8c5ae0' })),
    ...(analysis.mood ? [{ label: analysis.mood, icon: <Palette size={11} />, color: '#e08c5a' }] : []),
    ...(analysis.era ? [{ label: analysis.era, icon: <Clock size={11} />, color: '#5ae0a0' }] : []),
  ]

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid var(--border)',
      borderRadius: 12,
      padding: '12px 16px',
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      flexWrap: 'wrap',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: 'var(--accent)', fontSize: 12, fontWeight: 600 }}>
        <Zap size={13} />
        {total} results
      </div>

      {chips.length > 0 && (
        <>
          <div style={{ width: 1, height: 14, background: 'var(--border)' }} />
          <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
            {chips.map((c, i) => (
              <span key={i} style={{
                display: 'flex', alignItems: 'center', gap: 4,
                fontSize: 11, fontWeight: 500, padding: '3px 8px', borderRadius: 6,
                background: `${c.color}14`, color: c.color, border: `1px solid ${c.color}25`,
              }}>
                {c.icon} {c.label}
              </span>
            ))}
          </div>
        </>
      )}

      <div style={{ marginLeft: 'auto', display: 'flex', gap: 12, fontSize: 11, color: 'var(--text3)' }}>
        {latencyMs && <span>{latencyMs.toFixed(0)}ms</span>}
        <span style={{ background: 'var(--surface)', padding: '2px 7px', borderRadius: 4 }}>
          {algorithm.replace(/_/g, ' ')}
        </span>
      </div>
    </div>
  )
}
