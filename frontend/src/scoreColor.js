// Maps a -100..100 composite score to a red -> gray -> green background/text pair.
export function scoreToColors(score) {
  const clamped = Math.max(-100, Math.min(100, score))
  const t = clamped / 100 // -1..1

  if (t >= 0) {
    const g = Math.round(220 - t * 60)
    return { bg: `rgba(16, 163, 74, ${0.12 + t * 0.55})`, text: '#0f6832', border: `rgba(16, 163, 74, ${0.3 + t * 0.5})` }
  }
  const at = Math.abs(t)
  return { bg: `rgba(220, 38, 38, ${0.12 + at * 0.55})`, text: '#9f1c1c', border: `rgba(220, 38, 38, ${0.3 + at * 0.5})` }
}

export function scoreLabel(score) {
  if (score >= 40) return 'Strongly Bullish'
  if (score >= 12) return 'Bullish'
  if (score > -12) return 'Neutral'
  if (score > -40) return 'Bearish'
  return 'Strongly Bearish'
}
