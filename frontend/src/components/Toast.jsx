export default function Toast({ show, msg, type }) {
  return (
    <div
      className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-xl text-sm font-medium shadow-lg transition-all duration-300 pointer-events-none ${
        show ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      } ${
        type === 'error'
          ? 'bg-red-600 text-white'
          : 'bg-zinc-900 text-white'
      }`}
    >
      {msg}
    </div>
  )
}
