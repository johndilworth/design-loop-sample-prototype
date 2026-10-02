import { vendors as seedVendors } from './data'
// Vendor status changes made in the review step, kept in sessionStorage (prototype only, no backend).
const KEY = 'nw.vendorStatus'
const ADDED = 'nw.addedVendors' // cycle 4: vendors created with the "Add vendor" form
function read(key, fallback) {
  try { return JSON.parse(sessionStorage.getItem(key)) || fallback } catch { return fallback }
}
function write(key, value) {
  try { sessionStorage.setItem(key, JSON.stringify(value)) } catch { /* storage unavailable */ }
}
export function setVendorStatus(id, status) {
  write(KEY, { ...read(KEY, {}), [id]: status })
}
export const withStatus = (v) => (v ? { ...v, status: read(KEY, {})[v.id] || v.status } : v)
// Seed vendors + vendors added this session.
export const allVendors = () => [...seedVendors, ...read(ADDED, [])]
export const findAnyVendor = (id) => allVendors().find((v) => v.id === id)
export const totalSpendAll = () => allVendors().reduce((s, v) => s + (v.spend || 0), 0)
export function addVendor(fields) {
  const added = read(ADDED, [])
  const v = { ...fields, id: `v-${5000 + added.length + 1}`, status: 'Pending review' }
  write(ADDED, [...added, v])
  return v
}
