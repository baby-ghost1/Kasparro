export default function Charts({ data }) {
  const candidates = data.eligible_candidates
  const { total_resumes, eligible, rejected, failed } = data.batch_summary

  const ranges = { '80-100': 0, '60-79': 0, '40-59': 0, '0-39': 0 }
  candidates.forEach(c => {
    if (c.total_score >= 80) ranges['80-100']++
    else if (c.total_score >= 60) ranges['60-79']++
    else if (c.total_score >= 40) ranges['40-59']++
    else ranges['0-39']++
  })
  const maxR = Math.max(...Object.values(ranges), 1)
  const barColors = ['bg-zinc-900', 'bg-zinc-600', 'bg-zinc-400', 'bg-zinc-300']

  const circ = 2 * Math.PI * 48
  const eligOffset = circ - (eligible / total_resumes) * circ

  return (
    <div className="grid md:grid-cols-2 gap-3 mt-4">
      <div className="bg-white border border-zinc-200 rounded-xl p-5">
        <h4 className="text-xs font-semibold text-zinc-900 mb-4">Score Distribution</h4>
        <div className="flex flex-col gap-2.5">
          {Object.entries(ranges).map(([label, count], i) => (
            <div key={label} className="flex items-center gap-3">
              <span className="text-xs text-zinc-400 w-12 text-right tabular-nums">{label}</span>
              <div className="flex-1 h-5 bg-zinc-100 rounded-md overflow-hidden">
                <div
                  className={`h-full ${barColors[i]} rounded-md transition-all duration-700 flex items-center justify-end pr-2`}
                  style={{ width: `${(count / maxR) * 100}%` }}
                >
                  {count > 0 && <span className="text-[10px] text-white font-medium">{count}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white border border-zinc-200 rounded-xl p-5">
        <h4 className="text-xs font-semibold text-zinc-900 mb-4">Pipeline Results</h4>
        <div className="flex items-center gap-6">
          <svg className="w-24 h-24 shrink-0" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="48" fill="none" stroke="#f4f4f5" strokeWidth="10" />
            <circle cx="60" cy="60" r="48" fill="none" stroke="#16a34a" strokeWidth="10"
              strokeDasharray={circ} strokeDashoffset={eligOffset} strokeLinecap="round"
              style={{ transform: 'rotate(-90deg)', transformOrigin: 'center', transition: 'stroke-dashoffset 1s ease' }} />
          </svg>
          <div className="flex flex-col gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="text-zinc-600">Eligible ({eligible})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-zinc-600">Rejected ({rejected})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-zinc-300" />
              <span className="text-zinc-600">Failed ({failed})</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
