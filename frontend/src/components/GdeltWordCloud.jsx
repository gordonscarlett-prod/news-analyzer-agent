import { useState } from 'react'

// GDELT uses FIPS 10-4 country codes for the LOC param.
const LOCATIONS = [
  { code: 'US', label: 'United States' },
  { code: 'UK', label: 'United Kingdom' },
  { code: 'GM', label: 'Germany' },
  { code: 'FR', label: 'France' },
  { code: 'CH', label: 'China' },
  { code: 'JA', label: 'Japan' },
  { code: 'IN', label: 'India' },
  { code: 'RS', label: 'Russia' },
  { code: 'BR', label: 'Brazil' },
  { code: 'SA', label: 'Saudi Arabia' },
  { code: 'IR', label: 'Iran' },
  { code: 'IS', label: 'Israel' },
  { code: 'EG', label: 'Egypt' },
  { code: 'TU', label: 'Turkey' },
  { code: 'UP', label: 'Ukraine' },
  { code: 'NI', label: 'Nigeria' },
  { code: 'SF', label: 'South Africa' },
  { code: 'MX', label: 'Mexico' },
  { code: 'CA', label: 'Canada' },
  { code: 'AS', label: 'Australia' },
  { code: 'KS', label: 'South Korea' },
]

export default function GdeltWordCloud() {
  const [loc, setLoc] = useState('NI')

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <h2 className="text-lg font-semibold">GDELT News Word Cloud</h2>
        <select className="input w-auto" value={loc} onChange={e => setLoc(e.target.value)}>
          {LOCATIONS.map(l => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
      </div>
      <div className="flex justify-center">
        <iframe
          key={loc}
          src={`https://api.gdeltproject.org/api/v1/dash_thematicwordcloud/dash_thematicwordcloud?LOC=${loc}&OUTPUT=viz&VAR=trendall`}
          height="500"
          width="500"
          scrolling="no"
          title={`GDELT trending topics word cloud — ${LOCATIONS.find(l => l.code === loc)?.label}`}
        />
      </div>
    </div>
  )
}
