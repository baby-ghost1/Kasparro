import './Toast.css'

export default function Toast({ show, msg, type }) {
  return (
    <div className={`toast ${type} ${show ? 'show' : ''}`}>
      {msg}
    </div>
  )
}
