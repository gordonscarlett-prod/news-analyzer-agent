// Squarified treemap (Bruls, Huizing & van Wijk, 1999).
// Lays out `items` (each needs a positive `.weight`) inside a w×h rect,
// keeping tiles as close to square as the packing allows — same idea
// Finviz's map uses for sizing tiles by market weight.

function rowSum(row) {
  return row.reduce((s, d) => s + d.area, 0)
}

function worstRatio(row, side) {
  if (row.length === 0) return Infinity
  const sum = rowSum(row)
  const areas = row.map(d => d.area)
  const rmax = Math.max(...areas)
  const rmin = Math.min(...areas)
  return Math.max((side * side * rmax) / (sum * sum), (sum * sum) / (side * side * rmin))
}

function layoutRow(row, rect, results) {
  const sum = rowSum(row)
  if (rect.w >= rect.h) {
    // Vertical strip on the left; tiles stacked top-to-bottom within it.
    const stripW = sum / rect.h
    let cy = rect.y
    for (const d of row) {
      const tileH = (d.area / sum) * rect.h
      results.push({ ...d, x: rect.x, y: cy, w: stripW, h: tileH })
      cy += tileH
    }
    return { x: rect.x + stripW, y: rect.y, w: rect.w - stripW, h: rect.h }
  }
  // Horizontal strip on top; tiles laid left-to-right within it.
  const stripH = sum / rect.w
  let cx = rect.x
  for (const d of row) {
    const tileW = (d.area / sum) * rect.w
    results.push({ ...d, x: cx, y: rect.y, w: tileW, h: stripH })
    cx += tileW
  }
  return { x: rect.x, y: rect.y + stripH, w: rect.w, h: rect.h - stripH }
}

export function squarify(items, w, h) {
  const sorted = [...items].sort((a, b) => b.weight - a.weight)
  const total = sorted.reduce((s, d) => s + d.weight, 0)
  const scale = total > 0 ? (w * h) / total : 0
  let remaining = sorted.map(d => ({ ...d, area: d.weight * scale }))

  const results = []
  let rect = { x: 0, y: 0, w, h }
  let row = []

  while (remaining.length) {
    const side = Math.min(rect.w, rect.h)
    const next = remaining[0]
    const candidate = [...row, next]
    if (row.length === 0 || worstRatio(candidate, side) <= worstRatio(row, side)) {
      row = candidate
      remaining = remaining.slice(1)
    } else {
      rect = layoutRow(row, rect, results)
      row = []
    }
    if (remaining.length === 0 && row.length) {
      rect = layoutRow(row, rect, results)
      row = []
    }
  }

  return results
}
