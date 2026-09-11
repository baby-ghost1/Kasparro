import { useState } from 'react'
import StatsGrid from './StatsGrid'
import Charts from './Charts'
import CandidateCard from './CandidateCard'
import RejectedList from './RejectedList'
import './Dashboard.css'

export default function Dashboard({ data, onRescan }) {
  const [tab, setTab] = useState('eligible')

  return (
    <section className="dashboard">
      <div className="dash-header">
        <h2>Results</h2>
        <button className="btn-ghost" onClick={onRescan}>↻ New Scan</button>
      </div>

      <StatsGrid summary={data.batch_summary} />
      <Charts data={data} />

      <div className="tab-nav">
        <button className={`tab-btn ${tab === 'eligible' ? 'active' : ''}`} onClick={() => setTab('eligible')}>
          🏆 Eligible <span className="tab-count">{data.eligible_candidates.length}</span>
        </button>
        <button className={`tab-btn ${tab === 'rejected' ? 'active' : ''}`} onClick={() => setTab('rejected')}>
          ❌ Rejected <span className="tab-count">{data.rejected_candidates.length}</span>
        </button>
      </div>

      {tab === 'eligible' ? (
        <div className="candidates-list">
          {data.eligible_candidates.map(c => (
            <CandidateCard key={c.filename} candidate={c} />
          ))}
        </div>
      ) : (
        <RejectedList rejected={data.rejected_candidates} />
      )}
    </section>
  )
}
