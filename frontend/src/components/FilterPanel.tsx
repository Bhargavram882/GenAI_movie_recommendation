import { useState } from 'react'
import { SlidersHorizontal, X } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { useRecommendations } from '../hooks/useRecommendations'

const GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'Animation', 'Documentary', 'Crime', 'Fantasy', 'Mystery']

export default function FilterPanel() {
  const [open, setOpen] = useState(false)
  const { filters, setFilters, resetFilters } = useAppStore()
  const { search } = useRecommendations()

  const hasFilters = Object.keys(filters).some(k => (filters as any)[k])

  const toggleGenre = (g: string) => {
    const current = filters.genres || []
    const updated = current.includes(g) ? current.filter(x => x !== g) : [...current, g]
    setFilters({ ...filters, genres: updated.length > 0 ? updated : undefined })
  }

  const apply = () => { setOpen(false); search() }

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '10px 16px', borderRadius: 10,
          background: hasFilters ? 'rgba(232,201,122,0.1)' : 'var(--surface)',
          border: `1px solid ${hasFilters ? 'rgba(232,201,122,0.3)' : 'var(--border)'}`,
          color: hasFilters ? 'var(--accent)' : 'var(--text2)',
          fontSize: 13, fontWeight: 500, transition: 'all 0.15s',
        }}
      >
        <SlidersHorizontal size={15} />
        Filters {hasFilters && <span style={{ background: 'var(--accent)', color: '#0a0a0a', borderRadius: 4, padding: '1px 6px', fontSize: 11 }}>ON</span>}
      </button>

      {open && (
        <div style={{
          position: 'absolute', top: 'calc(100% + 8px)', right: 0, zIndex: 100,
          background: 'var(--bg2)',
          border: '1px solid var(--border2)',
          borderRadius: 14, padding: 20, width: 340,
          boxShadow: '0 24px 64px rgba(0,0,0,0.7)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontWeight: 600, fontSize: 15 }}>Refine Results</span>
            <button onClick={() => setOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text3)', padding: 0 }}>
              <X size={16} />
            </button>
          </div>

          {/* Genres */}
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 12, color: 'var(--text3)', letterSpacing: '0.06em', marginBottom: 8, display: 'block' }}>GENRES</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {GENRES.map(g => {
                const sel = (filters.genres || []).includes(g)
                return (
                  <button key={g} onClick={() => toggleGenre(g)} style={{
                    padding: '5px 10px', borderRadius: 7, fontSize: 12, fontWeight: 500,
                    background: sel ? 'rgba(232,201,122,0.15)' : 'var(--surface)',
                    border: `1px solid ${sel ? 'rgba(232,201,122,0.4)' : 'var(--border)'}`,
                    color: sel ? 'var(--accent)' : 'var(--text2)',
                    transition: 'all 0.12s',
                  }}>
                    {g}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Year Range */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 16 }}>
            {(['year_min', 'year_max'] as const).map((field, i) => (
              <div key={field}>
                <label style={{ fontSize: 12, color: 'var(--text3)', letterSpacing: '0.06em', display: 'block', marginBottom: 5 }}>
                  {i === 0 ? 'FROM YEAR' : 'TO YEAR'}
                </label>
                <input
                  type="number"
                  placeholder={i === 0 ? '1970' : '2024'}
                  value={(filters as any)[field] || ''}
                  onChange={e => setFilters({ ...filters, [field]: e.target.value ? Number(e.target.value) : undefined })}
                  style={{
                    width: '100%', background: 'var(--surface)', border: '1px solid var(--border)',
                    borderRadius: 8, padding: '8px 10px', fontSize: 13, color: 'var(--text)',
                    outline: 'none',
                  }}
                />
              </div>
            ))}
          </div>

          {/* Min Rating */}
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: 12, color: 'var(--text3)', letterSpacing: '0.06em', display: 'block', marginBottom: 5 }}>
              MIN RATING: {filters.min_rating ?? 0}/10
            </label>
            <input type="range" min={0} max={9} step={0.5}
              value={filters.min_rating ?? 0}
              onChange={e => setFilters({ ...filters, min_rating: Number(e.target.value) || undefined })}
              style={{ width: '100%', accentColor: 'var(--accent)' }}
            />
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={() => { resetFilters(); setOpen(false); }} style={{
              flex: 1, padding: '9px 0', borderRadius: 8, fontSize: 13, fontWeight: 500,
              background: 'transparent', border: '1px solid var(--border)', color: 'var(--text2)',
            }}>
              Reset
            </button>
            <button onClick={apply} style={{
              flex: 2, padding: '9px 0', borderRadius: 8, fontSize: 13, fontWeight: 500,
              background: 'var(--accent)', border: 'none', color: '#0a0a0a',
            }}>
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
