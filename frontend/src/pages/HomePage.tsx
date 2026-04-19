import { Film, Cpu, Database, Zap } from 'lucide-react'
import SearchBar from '../components/SearchBar'
import MovieCard from '../components/MovieCard'
import FilterPanel from '../components/FilterPanel'
import QueryInsights from '../components/QueryInsights'
import WatchHistory from '../components/WatchHistory'
import { useAppStore } from '../store/useAppStore'
import { useRecommendations } from '../hooks/useRecommendations'

const QUICK_SEARCHES = [
  'Cerebral sci-fi like Arrival',
  'Cozy rainy day movies',
  'Dark comedies from A24',
  'Epic war films',
  'Japanese animated films',
  'Cult classics from the 80s',
]

export default function HomePage() {
  const { results, isLoading, error } = useAppStore()
  const { search } = useRecommendations()

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{
        borderBottom: '1px solid var(--border)',
        padding: '16px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backdropFilter: 'blur(8px)',
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(8,8,16,0.85)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'linear-gradient(135deg, var(--accent), #c9a84c)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Film size={17} color="#0a0a0a" />
          </div>
          <span style={{ fontSize: 18, fontWeight: 600, letterSpacing: '-0.01em' }}>CineMate</span>
          <span style={{
            fontSize: 10, fontWeight: 600, padding: '2px 7px', borderRadius: 4,
            background: 'rgba(232,201,122,0.12)', color: 'var(--accent)',
            letterSpacing: '0.05em',
          }}>AI</span>
        </div>

        <div style={{ display: 'flex', gap: 20, fontSize: 12, color: 'var(--text3)' }}>
          {[
            { icon: <Cpu size={12} />, label: 'GPT-4o' },
            { icon: <Database size={12} />, label: 'Pinecone 10K+' },
            { icon: <Zap size={12} />, label: '<200ms' },
          ].map(({ icon, label }) => (
            <span key={label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              {icon} {label}
            </span>
          ))}
        </div>
      </header>

      {/* Hero / Search */}
      {!results && (
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '80px 24px',
          textAlign: 'center',
        }}>
          {/* Ambient glow */}
          <div style={{
            position: 'absolute',
            width: 600, height: 600,
            background: 'radial-gradient(circle, rgba(232,201,122,0.06) 0%, transparent 70%)',
            pointerEvents: 'none',
            top: '20%', left: '50%', transform: 'translateX(-50%)',
          }} />

          <h1 style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: 'clamp(36px, 6vw, 68px)',
            fontWeight: 400,
            lineHeight: 1.1,
            letterSpacing: '-0.02em',
            marginBottom: 16,
            maxWidth: 700,
          }}>
            Find your next<br />
            <em style={{ fontStyle: 'italic', color: 'var(--accent)' }}>perfect film</em>
          </h1>

          <p style={{
            fontSize: 17, color: 'var(--text2)', marginBottom: 48,
            maxWidth: 480, lineHeight: 1.6,
          }}>
            Describe what you're in the mood for in plain English.
            Our AI searches 10,000+ films semantically.
          </p>

          <SearchBar />

          {/* Quick searches */}
          <div style={{ marginTop: 28, display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 600 }}>
            {QUICK_SEARCHES.map(q => (
              <button
                key={q}
                onClick={() => search(q)}
                style={{
                  padding: '7px 14px', borderRadius: 20, fontSize: 13,
                  background: 'var(--surface)', border: '1px solid var(--border)',
                  color: 'var(--text2)', transition: 'all 0.15s', cursor: 'pointer',
                }}
                onMouseEnter={e => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border2)'
                  ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--text)'
                }}
                onMouseLeave={e => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)'
                  ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--text2)'
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results View */}
      {results && (
        <div style={{ flex: 1, maxWidth: 1280, width: '100%', margin: '0 auto', padding: '32px 24px' }}>
          {/* Search bar + filter row */}
          <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 20 }}>
            <div style={{ flex: 1 }}><SearchBar /></div>
            <FilterPanel />
          </div>

          <WatchHistory />

          <QueryInsights
            analysis={results.query_analysis}
            latencyMs={results.latency_ms}
            total={results.total}
            algorithm={results.algorithm}
          />

          {/* Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: 20,
            marginTop: 20,
          }}>
            {results.recommendations.map((movie, i) => (
              <MovieCard key={movie.id} movie={movie} index={i} />
            ))}
          </div>

          {results.recommendations.length === 0 && (
            <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text3)' }}>
              <Film size={40} style={{ marginBottom: 16, opacity: 0.3 }} />
              <p style={{ fontSize: 16 }}>No results found. Try a different query or adjust your filters.</p>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          margin: '24px auto', maxWidth: 500, textAlign: 'center',
          background: 'rgba(224,90,90,0.08)', border: '1px solid rgba(224,90,90,0.2)',
          borderRadius: 12, padding: '20px 24px', color: 'var(--red)',
        }}>
          <p style={{ fontWeight: 500, marginBottom: 4 }}>Something went wrong</p>
          <p style={{ fontSize: 13, opacity: 0.7 }}>{error}</p>
        </div>
      )}

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border)',
        padding: '20px 32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: 12,
        color: 'var(--text3)',
        flexWrap: 'wrap',
        gap: 8,
      }}>
        <span>CineMate AI — Hybrid GenAI Recommendation System</span>
        <div style={{ display: 'flex', gap: 16 }}>
          {['FastAPI', 'Pinecone', 'OpenAI', 'Redis', 'React', 'GCP'].map(t => (
            <span key={t} style={{
              background: 'var(--surface)', padding: '2px 8px', borderRadius: 4,
              border: '1px solid var(--border)',
            }}>{t}</span>
          ))}
        </div>
      </footer>
    </div>
  )
}
