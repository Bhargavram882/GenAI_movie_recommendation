import { History, Trash2, X } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { useRecommendations } from '../hooks/useRecommendations'

export default function WatchHistory() {
  const { watchHistory, removeFromHistory, clearHistory } = useAppStore()
  const { search } = useRecommendations()

  if (watchHistory.length === 0) return null

  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 12,
      padding: '14px 16px',
      marginBottom: 16,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600 }}>
          <History size={14} color="var(--text3)" />
          Watch History
          <span style={{
            background: 'var(--surface2)', padding: '1px 6px', borderRadius: 4,
            fontSize: 11, color: 'var(--text3)',
          }}>{watchHistory.length}</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => search()}
            style={{
              fontSize: 11, fontWeight: 500, padding: '4px 10px', borderRadius: 6,
              background: 'rgba(232,201,122,0.1)', border: '1px solid rgba(232,201,122,0.2)',
              color: 'var(--accent)', cursor: 'pointer',
            }}
          >
            Personalize
          </button>
          <button onClick={clearHistory} style={{
            background: 'none', border: 'none', color: 'var(--text3)', cursor: 'pointer',
          }}>
            <Trash2 size={13} />
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {watchHistory.slice(0, 8).map(id => (
          <span key={id} style={{
            display: 'flex', alignItems: 'center', gap: 4,
            fontSize: 11, padding: '3px 8px', borderRadius: 6,
            background: 'var(--surface2)', color: 'var(--text2)',
            border: '1px solid var(--border)',
          }}>
            {id.slice(0, 8)}…
            <button onClick={() => removeFromHistory(id)} style={{
              background: 'none', border: 'none', color: 'var(--text3)', cursor: 'pointer', padding: 0, lineHeight: 1,
            }}>
              <X size={10} />
            </button>
          </span>
        ))}
      </div>
    </div>
  )
}
