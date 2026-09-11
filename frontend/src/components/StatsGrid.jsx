import { useEffect, useRef } from 'react'
import './StatsGrid.css'

function AnimNum({ target }) {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    const start = performance.now()
    const dur = 800
    const tick = (now) => {
      const p = Math.min((now - start) / dur, 1)
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)))
      if (p < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [target])
  return <span ref={ref} className="stat-val">0</span>
}

export default function StatsGrid({ summary }) {
  const items = [
    { label: 'Total', value: summary.total_resumes, cls: 'total' },
    { label: 'Eligible', value: summary.eligible, cls: 'eligible' },
    { label: 'Rejected', value: summary.rejected, cls: 'rejected' },
    { label: 'Failed', value: summary.failed, cls: 'failed' },
  ]

  return (
    <div className="stats-grid">
      {items.map(i => (
        <div key={i.cls} className={`stat-card ${i.cls}`}>
          <span className="stat-label">{i.label}</span>
          <AnimNum target={i.value} />
        </div>
      ))}
    </div>
  )
}
