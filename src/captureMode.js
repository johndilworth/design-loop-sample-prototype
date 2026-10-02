// Journey capture mode: window.__DESIGN_LOOP_CAPTURE__ (set by journey/capture.mjs) or ?capture=1 in the URL.
// Used to freeze the home ASCII background and to keep toasts on screen until they are captured.
export function isCaptureMode() {
  if (typeof window === 'undefined') return false
  if (window.__DESIGN_LOOP_CAPTURE__) return true
  if (new URLSearchParams(window.location.search).get('capture') === '1') {
    window.__DESIGN_LOOP_CAPTURE__ = true // survive client-side navigation
    return true
  }
  return false
}
