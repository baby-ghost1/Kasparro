export default function RejectedList({ rejected }) {
  if (!rejected.length) {
    return <p className="text-sm text-zinc-400 text-center py-12">No rejected candidates.</p>
  }

  return (
    <div className="flex flex-col gap-2">
      {rejected.map((c, i) => (
        <div key={i} className="bg-white border border-zinc-200 rounded-xl p-4 flex items-center justify-between gap-4">
          <span className="text-sm font-medium text-zinc-900">{c.candidate_name || c.filename}</span>
          <span className="text-[11px] text-zinc-400 text-right">
            {(c.rejection_reasons || []).join('; ')}
          </span>
        </div>
      ))}
    </div>
  )
}
