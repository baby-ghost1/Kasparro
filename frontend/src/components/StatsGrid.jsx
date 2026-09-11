import { useEffect, useRef } from 'react'

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
  return <span ref={ref} className="text-2xl font-bold text-zinc-900 tabular-nums">0</span>
}

export default function StatsGrid({ summary }) {
  const items = [
    { label: 'Total', value: summary.total_resumes, color: 'bg-zinc-900' },
    { label: 'Eligible', value: summary.eligible, color: 'bg-emerald-500' },
    { label: 'Rejected', value: summary.rejected, color: 'bg-red-500' },
    { label: 'Failed', value: summary.failed, color: 'bg-zinc-400' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {items.map(i => (
        <div key={i.label} className="bg-white border border-zinc-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className={`w-2 h-2 rounded-full ${i.color}`} />
            <span className="text-xs text-zinc-500 font-medium">{i.label}</span>
          </div>
          <AnimNum target={i.value} />
        </div>
      ))}
    </div>
  )
}
