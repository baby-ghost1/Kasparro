import './Charts.css'

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
  const colors = ['var(--accent)', 'var(--green)', 'var(--amber)', 'var(--red)']

  const circ = 2 * Math.PI * 48
  const eligOffset = circ - (eligible / total_resumes) * circ

  return (
    <div className="charts">
      <div className="chart-card">
        <h4>Score Distribution</h4>
        <div className="bar-chart">
          {Object.entries(ranges).map(([label, count], i) => (
            <div key={label} className="bar-row">
              <span className="bar-label">{label}</span>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${(count / maxR) * 100}%`, background: colors[i] }}>
                  {count > 0 && count}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="chart-card">
        <h4>Pipeline Results</h4>
        <div className="donut-wrap">
          <svg className="donut" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,.04)" strokeWidth="10" />
            <circle cx="60" cy="60" r="48" fill="none" stroke="var(--green)" strokeWidth="10"
              strokeDasharray={circ} strokeDashoffset={eligOffset} strokeLinecap="round"
              style={{ transform: 'rotate(-90deg)', transformOrigin: 'center', transition: 'stroke-dashoffset 1s ease' }} />
          </svg>
          <div className="legend">
            <div className="legend-item"><span className="dot" style={{ background: 'var(--green)' }} /> Eligible ({eligible})</div>
            <div className="legend-item"><span className="dot" style={{ background: 'var(--red)' }} /> Rejected ({rejected})</div>
            <div className="legend-item"><span className="dot" style={{ background: '#52525b' }} /> Failed ({failed})</div>
          </div>
        </div>
      </div>
    </div>
  )
}
