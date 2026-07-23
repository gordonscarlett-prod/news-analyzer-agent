import { useNavigate } from 'react-router-dom'
import { scoreToColors } from '../scoreColor'

export default function SectorHeatmap({ sectors, date }) {
  const navigate = useNavigate()

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {sectors.map((s) => {
        const { bg, text, border } = scoreToColors(s.composite_score)
        return (
          <button
            key={s.sector}
            onClick={() => navigate(`/news?date=${date}&sector=${encodeURIComponent(s.sector)}`)}
            className="text-left rounded-xl p-4 border transition-transform hover:scale-[1.02]"
            style={{ backgroundColor: bg, borderColor: border }}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-800">{s.sector}</span>
              <span className="text-lg font-bold" style={{ color: text }}>
                {s.composite_score > 0 ? '+' : ''}{s.composite_score.toFixed(1)}
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-1">{s.article_count} article{s.article_count === 1 ? '' : 's'}</div>
            {s.top_articles?.length > 0 && (
              <div className="text-xs text-gray-600 mt-2 truncate">{s.top_articles[0].title}</div>
            )}
          </button>
        )
      })}
    </div>
  )
}
