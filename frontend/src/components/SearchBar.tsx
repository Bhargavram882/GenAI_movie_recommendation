import { useState, useRef, useEffect } from 'react'
import { Search, Sparkles, Loader2 } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { useRecommendations } from '../hooks/useRecommendations'

const SUGGESTIONS = [
  'Mind-bending sci-fi with unreliable narrators',
  'Heartwarming films about family from the 90s',
  'Dark psychological thrillers like Gone Girl',
  'Feel-good comedies set in Europe',
  'Epic historical dramas with stunning cinematography',
  'Quiet slow-burn romance films',
  'Animated films that adults will love',
]

export default function SearchBar() {
  const { query, setQuery, isLoading } = useAppStore()
  const { search } = useRecommendations()
  const [focused, setFocused] = useState(false)
  const [suggIdx, setSuggIdx] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const t = setInterval(() => setSuggIdx(i => (i + 1) % SUGGESTIONS.length), 3500)
    return () => clearInterval(t)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    search()
  }

  return (
    <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: 720 }}>
      <div style={{
        position: 'relative',
        background: focused ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.04)',
        border: `1px solid ${focused ? 'rgba(232,201,122,0.4)' : 'rgba(255,255,255,0.1)'}`,
        borderRadius: 16,
        transition: 'all 0.2s ease',
        boxShadow: focused ? '0 0 0 3px rgba(232,201,122,0.08), 0 8px 32px rgba(0,0,0,0.4)' : '0 4px 16px rgba(0,0,0,0.3)',
      }}>
        <div style={{
          position: 'absolute', left: 20, top: '50%', transform: 'translateY(-50%)',
          color: focused ? 'var(--accent)' : 'var(--text3)',
          transition: 'color 0.2s',
          pointerEvents: 'none',
        }}>
          <Search size={20} />
        </div>

        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={SUGGESTIONS[suggIdx]}
          style={{
            width: '100%',
            background: 'transparent',
            border: 'none',
            outline: 'none',
            padding: '20px 140px 20px 56px',
            fontSize: 16,
            color: 'var(--text)',
            caretColor: 'var(--accent)',
          }}
        />

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          style={{
            position: 'absolute',
            right: 8,
            top: '50%',
            transform: 'translateY(-50%)',
            background: query.trim() && !isLoading ? 'var(--accent)' : 'rgba(255,255,255,0.06)',
            color: query.trim() && !isLoading ? '#0a0a0a' : 'var(--text3)',
            border: 'none',
            borderRadius: 10,
            padding: '10px 20px',
            fontSize: 14,
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            transition: 'all 0.2s',
            cursor: query.trim() && !isLoading ? 'pointer' : 'not-allowed',
          }}
        >
          {isLoading
            ? <><Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> Finding...</>
            : <><Sparkles size={15} /> Discover</>
          }
        </button>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </form>
  )
}
