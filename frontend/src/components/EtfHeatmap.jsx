import { useEffect, useState } from 'react'
import { getEtfQuotes } from '../api'
import { pctChangeToColors } from '../scoreColor'
import { squarify } from '../treemap'

// Canvas is a fixed unit space; tiles are positioned as percentages of it so
// the layout stays responsive without needing to remeasure on resize.
const CANVAS_W = 1000
const CANVAS_H = 420

function tileSizeClass(weight) {
  if (weight >= 8) return { ticker: 'text-lg font-bold', pct: 'text-sm font-medium', showPct: true }
  if (weight >= 3) return { ticker: 'text-sm font-semibold', pct: 'text-xs font-medium', showPct: true }
  return { ticker: 'text-xs font-semibold', pct: '', showPct: false }
}

export default function EtfHeatmap() {
  const [etfs, setEtfs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getEtfQuotes()
      .then(d => setEtfs(d.etfs))
      .catch(() => setError('Could not load ETF quotes.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Sector ETF Heatmap</h2>
        <span className="text-xs text-gray-400">Daily % change · sized by sector weight</span>
      </div>

      {loading ? (
        <div className="text-gray-500 py-16 text-center">Loading…</div>
      ) : error ? (
        <div className="text-red-600 py-8 text-center">{error}</div>
      ) : (
        <div className="relative w-full" style={{ paddingTop: `${(CANVAS_H / CANVAS_W) * 100}%` }}>
          <div className="absolute inset-0">
            {squarify(etfs.map(e => ({ ...e, weight: e.weight || 0.1 })), CANVAS_W, CANVAS_H).map(tile => {
              const colors = pctChangeToColors(tile.percent_change)
              const sizing = tileSizeClass(tile.weight)
              return (
                <button
                  key={tile.ticker}
                  type="button"
                  className="group absolute flex flex-col items-center justify-center transition-transform hover:z-20 hover:scale-[1.03] focus:z-20 focus:outline-none"
                  style={{
                    left: `${(tile.x / CANVAS_W) * 100}%`,
                    top: `${(tile.y / CANVAS_H) * 100}%`,
                    width: `${(tile.w / CANVAS_W) * 100}%`,
                    height: `${(tile.h / CANVAS_H) * 100}%`,
                    backgroundColor: colors.bg,
                    border: `1px solid ${colors.border}`,
                    boxSizing: 'border-box',
                    margin: '-0.5px',
                  }}
                >
                  <span className={sizing.ticker} style={{ color: colors.text }}>{tile.ticker}</span>
                  {sizing.showPct && (
                    <span className={sizing.pct} style={{ color: colors.text }}>
                      {tile.percent_change == null ? '—' : `${tile.percent_change > 0 ? '+' : ''}${tile.percent_change.toFixed(2)}%`}
                    </span>
                  )}

                  <div
                    role="tooltip"
                    className="pointer-events-none absolute bottom-full left-1/2 mb-2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-gray-900 px-3 py-2 text-xs text-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100 group-focus:opacity-100"
                  >
                    <div className="font-semibold">{tile.ticker} — {tile.sector}</div>
                    <div>Price: {tile.price != null ? `$${tile.price.toFixed(2)}` : 'n/a'}</div>
                    <div>Change: {tile.change != null ? `${tile.change > 0 ? '+' : ''}${tile.change.toFixed(2)}` : 'n/a'} ({tile.percent_change != null ? `${tile.percent_change > 0 ? '+' : ''}${tile.percent_change.toFixed(2)}%` : 'n/a'})</div>
                    <div>Sector weight: {tile.weight.toFixed(1)}%</div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
