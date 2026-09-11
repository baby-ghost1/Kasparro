import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Dashboard from './components/Dashboard'
import Toast from './components/Toast'
import { getResults } from './api'

export default function App() {
  const [data, setData] = useState(null)
  const [toast, setToast] = useState({ show: false, msg: '', type: 'success' })

  const showToast = (msg, type = 'success') => {
    setToast({ show: true, msg, type })
    setTimeout(() => setToast({ show: false, msg: '', type: 'success' }), 3500)
  }

  useEffect(() => {
    getResults()
      .then(d => { if (d.batch_summary) setData(d) })
      .catch(() => {})
  }, [])

  return (
    <div className="min-h-screen flex flex-col bg-[#fafafa]">
      <Navbar />
      <main className="flex-1">
        {!data ? (
          <Hero onData={setData} showToast={showToast} />
        ) : (
          <Dashboard data={data} onRescan={() => setData(null)} />
        )}
      </main>
      <Toast {...toast} />
      <footer className="text-center py-6 text-xs text-zinc-400 border-t border-zinc-200">
        ResumeAI — AI Resume Screening & Ranking System
      </footer>
    </div>
  )
}
