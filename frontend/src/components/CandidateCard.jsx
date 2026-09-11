import { useState } from 'react'

const rankStyle = (rank) => {
  if (rank === 1) return 'bg-zinc-900 text-white'
  if (rank === 2) return 'bg-zinc-600 text-white'
  if (rank === 3) return 'bg-zinc-400 text-white'
  return 'bg-zinc-100 text-zinc-500'
}

const ScoreBar = ({ label, value, max, barClass }) => (
  <div className="flex items-center gap-2">
    <span className="text-[10px] text-zinc-400 w-8 text-right">{label}</span>
    <div className="flex-1 h-1.5 bg-zinc-100 rounded-full overflow-hidden">
      <div className={`h-full rounded-full ${barClass}`} style={{ width: `${(value / max) * 100}%` }} />
    </div>
    <span className="text-[10px] text-zinc-400 w-8 tabular-nums">{value}/{max}</span>
  </div>
)

export default function CandidateCard({ candidate: c }) {
  const [open, setOpen] = useState(false)
  const sb = c.score_breakdown
  const skills = (c.matched_skills || []).slice(0, 8)

  return (
    <div
      className={`bg-white border border-zinc-200 rounded-xl overflow-hidden transition-all hover:border-zinc-300 ${open ? 'shadow-sm' : ''}`}
    >
      <div
        className="flex items-center justify-between p-4 cursor-pointer select-none"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-3">
          <span className={`w-8 h-8 rounded-lg text-xs font-bold flex items-center justify-center ${rankStyle(c.rank)}`}>
            #{c.rank}
          </span>
          <div>
            <div className="text-sm font-semibold text-zinc-900">{c.candidate_name}</div>
            <div className="text-[11px] text-zinc-400">{c.email || ''}</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-zinc-900 tabular-nums">{c.total_score}</span>
          <svg className={`w-4 h-4 text-zinc-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <div className="px-4 pb-3 flex flex-col gap-1.5">
        <ScoreBar label="AI" value={sb.ai_project_depth} max={40} barClass="bg-zinc-900" />
        <ScoreBar label="Py" value={sb.python_backend} max={30} barClass="bg-zinc-700" />
        <ScoreBar label="Cloud" value={sb.cloud_fullstack} max={15} barClass="bg-zinc-500" />
        <ScoreBar label="GH" value={sb.github} max={10} barClass="bg-zinc-400" />
        <ScoreBar label="Eng" value={sb.engineering_depth} max={5} barClass="bg-zinc-300" />
      </div>

      {skills.length > 0 && (
        <div className="px-4 pb-3 flex flex-wrap gap-1.5">
          {skills.map(s => (
            <span key={s} className="px-2 py-0.5 bg-zinc-100 text-zinc-600 text-[10px] rounded-md font-medium">
              {s}
            </span>
          ))}
        </div>
      )}

      <div className="px-4 pb-3 flex flex-col gap-1">
        {(c.strengths || []).slice(0, 3).map((s, i) => (
          <div key={i} className="text-[11px] text-emerald-700 bg-emerald-50 rounded-md px-2.5 py-1.5">
            {s}
          </div>
        ))}
        {(c.concerns || []).slice(0, 2).map((s, i) => (
          <div key={i} className="text-[11px] text-amber-700 bg-amber-50 rounded-md px-2.5 py-1.5">
            {s}
          </div>
        ))}
      </div>

      {open && (
        <div className="border-t border-zinc-100 p-4 grid md:grid-cols-2 gap-4">
          <div>
            <h5 className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider mb-1.5">Project Summary</h5>
            <p className="text-xs text-zinc-600 leading-relaxed">{c.project_summary || 'N/A'}</p>
          </div>
          <div>
            <h5 className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider mb-1.5">GitHub</h5>
            <p className="text-xs text-zinc-600 leading-relaxed">{c.github_summary || 'No GitHub profile found'}</p>
          </div>
        </div>
      )}
    </div>
  )
}
