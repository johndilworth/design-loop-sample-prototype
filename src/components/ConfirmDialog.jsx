import { useEffect, useRef } from 'react'

// Minimal modal confirmation (cycle-3 feedback: Reject needs a second confirmation).
// Focus starts on Cancel, Tab/Shift+Tab cycle inside the dialog, Esc or the backdrop cancels,
// and focus returns to the element that opened it.
export default function ConfirmDialog({ title, children, confirmLabel, onConfirm, onCancel }) {
  const ref = useRef(null)
  useEffect(() => {
    const opener = document.activeElement
    const box = ref.current
    box.querySelector('button')?.focus()
    const onKey = (e) => {
      if (e.key === 'Escape') { e.preventDefault(); onCancel() }
      if (e.key === 'Tab') {
        const items = [...box.querySelectorAll('button, [href], input, textarea, select')]
        const first = items[0], last = items[items.length - 1]
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
      }
    }
    document.addEventListener('keydown', onKey)
    return () => { document.removeEventListener('keydown', onKey); opener?.focus?.() }
  }, [onCancel])
  return (
    <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onCancel() }}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-desc" ref={ref}>
        <h2 id="confirm-title">{title}</h2>
        <div id="confirm-desc">{children}</div>
        <div className="row">
          <button type="button" className="btn" onClick={onCancel}>Cancel</button>
          <button type="button" className="btn danger" onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  )
}
