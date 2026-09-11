import { useState } from 'react'
import { startScreening, getResults } from '../api'
import './Hero.css'

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
    <section className="hero">
      <h1>AI Resume<br />Screening Dashboard</h1>
      <p>Upload resumes and get AI-powered rankings with detailed score breakdowns.</p>

      <div className="upload-zone">
        <div className="upload-icon">📄</div>
        <h3>Screen Your Resumes</h3>
        <p className="upload-desc">Runs the screening pipeline on the <code>./resumes</code> directory</p>
        <button className="btn-primary" onClick={handleScreen} disabled={loading}>
          {loading ? '⏳ Screening...' : '🚀 Start Screening'}
        </button>
      </div>

      {loading && (
        <div className="progress-wrap">
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <span className="progress-text">{statusText}</span>
        </div>
      )}
    </section>
  )
}
