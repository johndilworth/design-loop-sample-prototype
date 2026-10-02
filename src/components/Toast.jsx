import { useEffect } from 'react'
import { isCaptureMode } from '../captureMode'

// Lower-left "growl" notification (cycle-3 feedback): × to dismiss, auto-dismisses after 3 s.
// In journey capture mode it stays until dismissed so the screenshot can include it.
export default function Toast({ message, onDismiss, duration = 3000 }) {
  useEffect(() => {
    if (!message || isCaptureMode()) return
    const t = setTimeout(onDismiss, duration)
    return () => clearTimeout(t)
  }, [message, onDismiss, duration])
  return (
    <div className="toast-region" role="status" aria-live="polite">
      {message && (
        <div className="toast">
          <span>{message}</span>
          <button type="button" className="toast-close" aria-label="Dismiss notification" onClick={onDismiss}>×</button>
        </div>
      )}
    </div>
  )
}
