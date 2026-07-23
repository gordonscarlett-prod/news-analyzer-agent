import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { getSectorTrend } from '../api'

const SECTORS = [
  'Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 'Communication Services',
  'Industrials', 'Consumer Staples', 'Energy', 'Utilities', 'Real Estate', 'Materials',
]

export default function Trends() {
  const [sector, setSector] = useState('Technology')
  const [days, setDays] = useState(30)
  const [points, setPoints] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getSectorTrend(sector, days)
      .then(d => setPoints(d.points))
      .finally(() => setLoading(false))
  }, [sector, days])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Sector Trends</h1>
        <p className="text-sm text-gray-500">How news-driven impact scores have moved over time</p>
      </div>

      <div className="card">
        <div className="flex items-center gap-4 mb-4 flex-wrap">
          <select className="input w-auto" value={sector} onChange={e => setSector(e.target.value)}>
            {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <div className="flex gap-1">
            {[7, 30, 90].map(d => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={days === d ? 'nav-link-active' : 'nav-link'}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="text-gray-500 py-16 text-center">Loading…</div>
        ) : points.length === 0 ? (
          <div className="text-gray-500 py-16 text-center">No data yet for {sector}. Run the pipeline for a few days to build a trend.</div>
        ) : (
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={points}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis domain={[-100, 100]} tick={{ fontSize: 12 }} />
              <Tooltip />
              <ReferenceLine y={0} stroke="#999" />
              <Line type="monotone" dataKey="composite_score" stroke="#3660f7" strokeWidth={2} dot={{ r: 3 }} name="Impact Score" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
