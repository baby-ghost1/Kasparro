import { useState } from 'react'
import './CandidateCard.css'

const rankStyle = (rank) => {
  if (rank === 1) return { background: 'linear-gradient(135deg,#fbbf24,#f59e0b)', color: '#000' }
  if (rank === 2) return { background: 'linear-gradient(135deg,#94a3b8,#64748b)', color: '#000' }
  if (rank === 3) return { background: 'linear-gradient(135deg,#cd7c2f,#a0522d)', color: '#fff' }
  return { background: 'var(--card)', color: 'var(--text2)', border: '1px solid var(--border)' }
}

const scoreBar = (label, value, max, gradient) => (
  <div className="sc-row">
    <span className="sc-label">{label}</span>
    <div className="sc-track">
      <div className="sc-fill" style={{ width: `${(value / max) * 100}%`, background: gradient }} />
    </div>
    <span className="sc-val">{value}/{max}</span>
  </div>
)

export default function CandidateCard({ candidate: c }) {
  const [open, setOpen] = useState(false)
  const sb = c.score_breakdown
  const skills = (c.matched_skills || []).slice(0, 8)

  return (
    <div className={`card ${open ? 'open' : ''}`} onClick={() => setOpen(!open)}>
      <div className="card-top">
        <div className="card-left">
          <div className="rank" style={rankStyle(c.rank)}>#{c.rank}</div>
          <div>
            <div className="name">{c.candidate_name}</div>
            <div className="email">{c.email || ''}</div>
          </div>
        </div>
        <div className="card-right">
          <div className="score">{c.total_score}</div>
          <span className="arrow">{open ? '▲' : '▼'}</span>
        </div>
      </div>

      <div className="score-bars">
        {scoreBar('AI', sb.ai_project_depth, 40, 'linear-gradient(90deg,var(--accent),var(--pink))')}
        {scoreBar('Py', sb.python_backend, 30, 'linear-gradient(90deg,var(--green),var(--cyan))')}
        {scoreBar('Cloud', sb.cloud_fullstack, 15, 'linear-gradient(90deg,var(--amber),var(--red))')}
        {scoreBar('GH', sb.github, 10, 'linear-gradient(90deg,#a855f7,#ec4899)')}
        {scoreBar('Eng', sb.engineering_depth, 5, 'linear-gradient(90deg,var(--cyan),var(--accent))')}
      </div>

      {skills.length > 0 && (
        <div className="skills">
          {skills.map(s => <span key={s} className="skill-tag">{s}</span>)}
        </div>
      )}

      <div className="insights">
        {(c.strengths || []).slice(0, 3).map((s, i) => (
          <div key={i} className="insight good">✓ {s}</div>
        ))}
        {(c.concerns || []).slice(0, 2).map((s, i) => (
          <div key={i} className="insight warn">⚠ {s}</div>
        ))}
      </div>

      <div className="details">
        <div className="detail-grid">
          <div className="detail-block">
            <h5>Project Summary</h5>
            <p>{c.project_summary || 'N/A'}</p>
          </div>
          <div className="detail-block">
            <h5>GitHub</h5>
            <p>{c.github_summary || 'No GitHub profile found'}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
