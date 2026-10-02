// Vendor status changes made in the review step, kept in sessionStorage (prototype only, no backend).
const KEY = 'nw.vendorStatus'
function load() {
  try { return JSON.parse(sessionStorage.getItem(KEY)) || {} } catch { return {} }
}
export function setVendorStatus(id, status) {
  try { sessionStorage.setItem(KEY, JSON.stringify({ ...load(), [id]: status })) } catch { /* storage unavailable */ }
}
export const withStatus = (v) => (v ? { ...v, status: load()[v.id] || v.status } : v)
