import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <div className="nav-logo">⚡</div>
        <span>ResumeAI</span>
      </div>
      <div className="nav-status">
        <span className="status-dot" />
        <span>Server Online</span>
      </div>
    </nav>
  )
}
