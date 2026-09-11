import { useState } from 'react'
import { startScreening, getResults } from '../api'

export default function Hero({ onData, showToast }) {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [statusText, setStatusText] = useState('')

  const steps = [
    [15, 'Discovering resumes...'],
    [30, 'Parsing PDF files...'],
    [50, 'Extracting candidate info...'],
    [65, 'Checking eligibility...'],
    [80, 'Scoring candidates...'],
    [90, 'Enriching GitHub data...'],
  ]

  const handleScreen = async () => {
    setLoading(true)
    setProgress(5)
    let stepIdx = 0

    const interval = setInterval(() => {
      if (stepIdx < steps.length) {
        setProgress(steps[stepIdx][0])
        setStatusText(steps[stepIdx][1])
        stepIdx++
      }
    }, 2500)

    try {
      const result = await startScreening()
      clearInterval(interval)
      setProgress(100)
      setStatusText('Done!')

      const data = await getResults()
      setTimeout(() => {
        onData(data)
        showToast(`Screened ${result.total_resumes} resumes — ${result.eligible} eligible`)
      }, 400)
    } catch (err) {
      clearInterval(interval)
      setProgress(0)
      setStatusText('')
      showToast('API unavailable — start the backend server', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="max-w-6xl mx-auto px-4 py-20 flex flex-col items-center text-center">
      <h1 className="text-4xl md:text-5xl font-bold text-zinc-900 tracking-tight leading-tight mb-4">
        AI Resume<br />Screening Dashboard
      </h1>
      <p className="text-zinc-500 text-base mb-12 max-w-md">
        Upload resumes and get AI-powered rankings with detailed score breakdowns.
      </p>

      <div className="w-full max-w-md bg-white border border-zinc-200 rounded-2xl p-8 shadow-sm">
        <div className="w-12 h-12 rounded-xl bg-zinc-100 flex items-center justify-center mx-auto mb-4">
          <svg className="w-5 h-5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        </div>
        <h3 className="text-sm font-semibold text-zinc-900 mb-1">Screen Your Resumes</h3>
        <p className="text-xs text-zinc-400 mb-6">
          Runs the screening pipeline on the <code className="bg-zinc-100 px-1.5 py-0.5 rounded text-zinc-600">./data/resumes</code> directory
        </p>
        <button
          onClick={handleScreen}
          disabled={loading}
          className="w-full h-10 rounded-lg bg-zinc-900 text-white text-sm font-medium hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
        >
          {loading ? 'Screening...' : 'Start Screening'}
        </button>
      </div>

      {loading && (
        <div className="w-full max-w-md mt-8">
          <div className="h-1.5 bg-zinc-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-zinc-900 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-zinc-400 mt-2 text-center">{statusText}</p>
        </div>
      )}
    </section>
  )
}
