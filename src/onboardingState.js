// Onboarding selections persisted in sessionStorage so Back keeps the previous choice highlighted.
const KEY = 'nw.onboarding'
export function loadOnboarding() {
  try { return JSON.parse(sessionStorage.getItem(KEY)) || {} } catch { return {} }
}
export function saveOnboarding(patch) {
  const next = { ...loadOnboarding(), ...patch }
  try { sessionStorage.setItem(KEY, JSON.stringify(next)) } catch { /* storage unavailable */ }
  return next
}
