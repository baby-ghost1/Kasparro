import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Dashboard from './components/Dashboard'
import Toast from './components/Toast'
import { getResults } from './api'
import './App.css'

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
    <div className="app">
      <Navbar />
      {!data ? (
        <Hero onData={setData} showToast={showToast} />
      ) : (
        <Dashboard data={data} onRescan={() => setData(null)} />
      )}
      <Toast {...toast} />
      <footer className="footer">ResumeAI — AI Resume Screening & Ranking System</footer>
    </div>
  )
}
