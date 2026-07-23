import { useEffect, useState, useCallback } from 'react'
import { RefreshCw } from 'lucide-react'
import { getDailyScore, runNow, getStatus } from '../api'
import { scoreToColors, scoreLabel } from '../scoreColor'
import SectorHeatmap from '../components/SectorHeatmap'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    try {
      setError(null)
      const result = await getDailyScore()
      setData(result)
    } catch (e) {
      setError('Could not load today\'s score. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleRunNow = async () => {
    setRunning(true)
    try {
      await runNow()
      // Poll status until the run completes, then reload the score.
      const started = Date.now()
      const poll = setInterval(async () => {
        const status = await getStatus()
        const latest = status.runs?.[0]
        const timedOut = Date.now() - started > 5 * 60 * 1000
        if ((latest && latest.status !== 'running') || timedOut) {
          clearInterval(poll)
          setRunning(false)
          load()
        }
      }, 4000)
    } catch (e) {
      setRunning(false)
    }
  }

  if (loading) return <div className="text-gray-500">Loading…</div>
  if (error) return <div className="card text-red-600">{error}</div>

  const overallColors = scoreToColors(data.overall_score)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Daily Market Impact — {data.date}</h1>
          <p className="text-sm text-gray-500">Sector-level equity impact score derived from today's news</p>
        </div>
        <button className="btn-primary inline-flex items-center gap-2" onClick={handleRunNow} disabled={running}>
          <RefreshCw size={16} className={running ? 'animate-spin' : ''} />
          {running ? 'Running…' : 'Run Now'}
        </button>
      </div>

      <div className="card">
        <div className="flex items-center gap-6 flex-wrap">
          <div
            className="w-28 h-28 rounded-full flex flex-col items-center justify-center border-4 shrink-0"
            style={{ borderColor: overallColors.border, backgroundColor: overallColors.bg }}
          >
            <span className="text-2xl font-bold" style={{ color: overallColors.text }}>
              {data.overall_score > 0 ? '+' : ''}{data.overall_score.toFixed(1)}
            </span>
            <span className="text-[10px] uppercase tracking-wide text-gray-500">Overall</span>
          </div>
          <div className="flex-1 min-w-[240px]">
            <div className="font-medium mb-1" style={{ color: overallColors.text }}>{scoreLabel(data.overall_score)}</div>
            <p className="text-sm text-gray-700">{data.narrative || 'No narrative yet — run the pipeline to generate today\'s briefing.'}</p>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Sectors</h2>
        <SectorHeatmap sectors={data.sectors} date={data.date} />
      </div>
    </div>
  )
}
