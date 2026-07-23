import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ExternalLink } from 'lucide-react'
import { getArticles } from '../api'
import { scoreToColors } from '../scoreColor'

const SECTORS = [
  'Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 'Communication Services',
  'Industrials', 'Consumer Staples', 'Energy', 'Utilities', 'Real Estate', 'Materials',
]

function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

export default function NewsFeed() {
  const [searchParams, setSearchParams] = useSearchParams()
  const date = searchParams.get('date') || todayStr()
  const sector = searchParams.get('sector') || ''
  const [minImpact, setMinImpact] = useState(0)
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getArticles({ date, sector: sector || undefined, min_impact: minImpact })
      .then(d => setArticles(d.articles))
      .finally(() => setLoading(false))
  }, [date, sector, minImpact])

  const updateParam = (key, value) => {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value); else next.delete(key)
    setSearchParams(next)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">News Feed</h1>
        <p className="text-sm text-gray-500">Articles behind the sector impact scores</p>
      </div>

      <div className="card">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <input type="date" className="input w-auto" value={date} onChange={e => updateParam('date', e.target.value)} />
          <select className="input w-auto" value={sector} onChange={e => updateParam('sector', e.target.value)}>
            <option value="">All sectors</option>
            {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select className="input w-auto" value={minImpact} onChange={e => setMinImpact(Number(e.target.value))}>
            <option value={0}>Any impact</option>
            <option value={3}>Impact ≥ 3</option>
            <option value={5}>Impact ≥ 5</option>
            <option value={7}>Impact ≥ 7</option>
          </select>
        </div>

        {loading ? (
          <div className="text-gray-500 py-16 text-center">Loading…</div>
        ) : articles.length === 0 ? (
          <div className="text-gray-500 py-16 text-center">No scored articles for this filter yet.</div>
        ) : (
          <div className="divide-y divide-gray-100">
            {articles.map(a => {
              const colors = scoreToColors(a.sentiment * 100)
              return (
                <div key={`${a.id}-${a.sector}`} className="py-4 flex items-start gap-4">
                  <div className="shrink-0 w-16 text-center">
                    <div className="text-lg font-bold" style={{ color: colors.text }}>{a.impact.toFixed(1)}</div>
                    <div className="text-[10px] uppercase text-gray-400">impact</div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <a href={a.url} target="_blank" rel="noreferrer" className="font-medium text-gray-900 hover:text-brand-600 inline-flex items-center gap-1">
                      {a.title} <ExternalLink size={13} className="text-gray-400" />
                    </a>
                    <div className="text-sm text-gray-500 mt-1">{a.rationale}</div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="badge" style={{ backgroundColor: colors.bg, color: colors.text }}>{a.sector}</span>
                      <span className="text-xs text-gray-400">{a.source}</span>
                      <span className="text-xs text-gray-400">·</span>
                      <span className="text-xs text-gray-400">{a.time_horizon}</span>
                      <span className="text-xs text-gray-400">·</span>
                      <span className="text-xs text-gray-400">confidence {(a.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
