import { useState } from 'react'
import StatsGrid from './StatsGrid'
import Charts from './Charts'
import CandidateCard from './CandidateCard'
import RejectedList from './RejectedList'

export default function Dashboard({ data, onRescan }) {
  const [tab, setTab] = useState('eligible')

  return (
    <section className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-xl font-semibold text-zinc-900">Results</h2>
        <button
          onClick={onRescan}
          className="h-8 px-3 text-xs font-medium text-zinc-600 bg-zinc-100 hover:bg-zinc-200 rounded-lg transition-colors cursor-pointer"
        >
          New Scan
        </button>
      </div>

      <StatsGrid summary={data.batch_summary} />
      <Charts data={data} />

      <div className="flex gap-1 bg-zinc-100 rounded-lg p-1 mb-6 mt-8">
        <button
          onClick={() => setTab('eligible')}
          className={`flex-1 h-8 text-xs font-medium rounded-md transition-colors cursor-pointer ${
            tab === 'eligible' ? 'bg-white text-zinc-900 shadow-sm' : 'text-zinc-500 hover:text-zinc-700'
          }`}
        >
          Eligible ({data.eligible_candidates.length})
        </button>
        <button
          onClick={() => setTab('rejected')}
          className={`flex-1 h-8 text-xs font-medium rounded-md transition-colors cursor-pointer ${
            tab === 'rejected' ? 'bg-white text-zinc-900 shadow-sm' : 'text-zinc-500 hover:text-zinc-700'
          }`}
        >
          Rejected ({data.rejected_candidates.length})
        </button>
      </div>

      {tab === 'eligible' ? (
        <div className="flex flex-col gap-3">
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
