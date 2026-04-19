import { useState } from 'react'
import { Star, Clock, Eye, ChevronDown, ChevronUp, Sparkles } from 'lucide-react'
import type { Movie } from '../types'
import { useAppStore } from '../store/useAppStore'

const TMDB_IMG = 'https://image.tmdb.org/t/p/w500'
const FALLBACK = 'https://via.placeholder.com/300x450/0f0f1a/444444?text=No+Poster'

const GENRE_COLORS: Record<string, string> = {
  Action: '#e05a5a', Adventure: '#e08c5a', Animation: '#5ae0a0',
  Comedy: '#e8c97a', Crime: '#a05ae0', Documentary: '#5a9ae0',
  Drama: '#e05a9a', Fantasy: '#5ae0d4', Horror: '#e05a5a',
  Mystery: '#8c5ae0', Romance: '#e05a8c', 'Science Fiction': '#5a9ae0',
  Thriller: '#c95ae0', Western: '#e0a05a',
}

interface Props {
  movie: Movie
  index: number
}

export default function MovieCard({ movie, index }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [imgError, setImgError] = useState(false)
  const { addToHistory, watchHistory } = useAppStore()
  const isWatched = watchHistory.includes(movie.id)

  const posterUrl = movie.poster_path && !imgError
    ? `${TMDB_IMG}${movie.poster_path}`
    : FALLBACK

  const scorePercent = Math.round(movie.score * 100)
  const scoreColor = scorePercent >= 85 ? '#5ae0a0' : scorePercent >= 70 ? '#e8c97a' : '#e0a05a'

  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      overflow: 'hidden',
      transition: 'all 0.25s ease',
      animation: `fadeSlideUp 0.4s ease ${index * 0.05}s both`,
      position: 'relative',
    }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLDivElement).style.border = '1px solid var(--border2)'
        ;(e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)'
        ;(e.currentTarget as HTMLDivElement).style.boxShadow = '0 16px 48px rgba(0,0,0,0.5)'
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLDivElement).style.border = '1px solid var(--border)'
        ;(e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)'
        ;(e.currentTarget as HTMLDivElement).style.boxShadow = 'none'
      }}
    >
      {/* Match score badge */}
      <div style={{
        position: 'absolute', top: 12, right: 12, zIndex: 2,
        background: 'rgba(0,0,0,0.75)',
        backdropFilter: 'blur(8px)',
        border: `1px solid ${scoreColor}40`,
        borderRadius: 8,
        padding: '4px 8px',
        fontSize: 12,
        fontWeight: 600,
        color: scoreColor,
      }}>
        {scorePercent}% match
      </div>

      {/* Poster */}
      <div style={{ position: 'relative', paddingTop: '56%', background: 'var(--bg3)' }}>
        <img
          src={posterUrl}
          onError={() => setImgError(true)}
          alt={movie.title}
          style={{
            position: 'absolute', inset: 0,
            width: '100%', height: '100%',
            objectFit: 'cover',
            opacity: 0.85,
          }}
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(to top, rgba(8,8,16,0.95) 0%, rgba(8,8,16,0.2) 60%, transparent 100%)',
        }} />

        {/* Bottom of poster */}
        <div style={{ position: 'absolute', bottom: 12, left: 12, right: 44 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.3, marginBottom: 4, color: 'var(--text)' }}>
            {movie.title}
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text2)' }}>
            {movie.year && <span>{movie.year}</span>}
            {movie.vote_average > 0 && (
              <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                <Star size={11} fill="var(--accent)" color="var(--accent)" />
                {movie.vote_average.toFixed(1)}
              </span>
            )}
            {movie.runtime && (
              <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                <Clock size={11} /> {movie.runtime}m
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: '14px 16px 16px' }}>
        {/* Genres */}
        {movie.genres.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 10 }}>
            {movie.genres.slice(0, 3).map(g => (
              <span key={g} style={{
                fontSize: 11, fontWeight: 500, padding: '3px 8px', borderRadius: 6,
                background: `${GENRE_COLORS[g] || '#5a9ae0'}18`,
                color: GENRE_COLORS[g] || '#5a9ae0',
                border: `1px solid ${GENRE_COLORS[g] || '#5a9ae0'}30`,
              }}>{g}</span>
            ))}
          </div>
        )}

        {/* AI Explanation */}
        {movie.explanation && (
          <div style={{
            background: 'rgba(232,201,122,0.05)',
            border: '1px solid rgba(232,201,122,0.12)',
            borderRadius: 8,
            padding: '10px 12px',
            marginBottom: 10,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 5 }}>
              <Sparkles size={12} color="var(--accent)" />
              <span style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 500, letterSpacing: '0.04em' }}>
                WHY YOU'LL LOVE IT
              </span>
            </div>
            <p style={{
              fontSize: 13, color: 'var(--text2)', lineHeight: 1.55,
              display: expanded ? 'block' : '-webkit-box',
              WebkitLineClamp: expanded ? undefined : 3,
              WebkitBoxOrient: 'vertical' as any,
              overflow: 'hidden',
            }}>
              {movie.explanation}
            </p>
            {movie.explanation.length > 150 && (
              <button onClick={() => setExpanded(!expanded)} style={{
                background: 'none', border: 'none', color: 'var(--accent)', fontSize: 12,
                marginTop: 4, display: 'flex', alignItems: 'center', gap: 3, padding: 0,
              }}>
                {expanded ? <><ChevronUp size={12} /> Less</> : <><ChevronDown size={12} /> More</>}
              </button>
            )}
          </div>
        )}

        {/* Director */}
        {movie.director && (
          <p style={{ fontSize: 12, color: 'var(--text3)', marginBottom: 10 }}>
            dir. <span style={{ color: 'var(--text2)' }}>{movie.director}</span>
          </p>
        )}

        {/* Actions */}
        <button
          onClick={() => isWatched ? null : addToHistory(movie.id)}
          style={{
            width: '100%', padding: '9px 0', borderRadius: 8, fontSize: 13, fontWeight: 500,
            background: isWatched ? 'rgba(90,224,160,0.08)' : 'rgba(255,255,255,0.05)',
            border: `1px solid ${isWatched ? 'rgba(90,224,160,0.25)' : 'var(--border)'}`,
            color: isWatched ? 'var(--green)' : 'var(--text2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            transition: 'all 0.15s',
            cursor: isWatched ? 'default' : 'pointer',
          }}
        >
          <Eye size={14} />
          {isWatched ? 'In your history' : 'Mark as watched'}
        </button>
      </div>

      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
