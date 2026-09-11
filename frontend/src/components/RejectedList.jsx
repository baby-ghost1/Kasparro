import './RejectedList.css'

export default function RejectedList({ rejected }) {
  if (!rejected.length) return <p className="empty">No rejected candidates.</p>

  return (
    <div className="rejected-list">
      {rejected.map((c, i) => (
        <div key={i} className="rejected-card">
          <span className="rejected-name">{c.candidate_name || c.filename}</span>
          <span className="rejected-reason">{(c.rejection_reasons || []).join('; ')}</span>
        </div>
      ))}
    </div>
  )
}
