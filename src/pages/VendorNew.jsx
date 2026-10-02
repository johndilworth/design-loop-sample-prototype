import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import useTitle from '../useTitle'
import { addVendor } from '../vendorState'

const RISKS = ['Low', 'Medium', 'High']
const EMPTY = { name: '', category: '', model: '', owner: '', risk: '', spend: '' }

// cycle-4 feedback: new screen with a form to add a vendor. Saved for this session only (prototype, no backend);
// returns to the list with an "added" toast (same router-state toast as the review step).
export default function VendorNew() {
  useTitle('Add vendor')
  const nav = useNavigate()
  const [f, setF] = useState(EMPTY)
  const set = (k) => (e) => setF((x) => ({ ...x, [k]: e.target.value }))
  const spend = Number(f.spend)
  const ready = f.name.trim() && f.category.trim() && f.owner.trim() && f.risk && f.spend !== '' && spend >= 0
  const submit = (e) => {
    e.preventDefault()
    if (!ready) return
    const v = addVendor({ name: f.name.trim(), category: f.category.trim(), model: f.model.trim() || '—',
      owner: f.owner.trim(), risk: f.risk, spend })
    nav('/vendors', { state: { toast: `${v.name} was added.` } })
  }
  return (
    <section className="card">
      <h1>Add a vendor</h1>
      <p className="muted">New vendors start as Pending review. Fields marked * are required.</p>
      <form onSubmit={submit} noValidate>
        <div className="form-grid">
          <div className="full"><label htmlFor="vn-name">Vendor name *</label><input id="vn-name" type="text" value={f.name} onChange={set('name')} /></div>
          <div><label htmlFor="vn-category">Category *</label><input id="vn-category" type="text" value={f.category} onChange={set('category')} placeholder="e.g. AI platform" /></div>
          <div><label htmlFor="vn-model">Model / service</label><input id="vn-model" type="text" value={f.model} onChange={set('model')} placeholder="e.g. Hosted LLM routing" /></div>
          <div><label htmlFor="vn-owner">Business owner *</label><input id="vn-owner" type="text" value={f.owner} onChange={set('owner')} /></div>
          <div>
            <label htmlFor="vn-risk">Risk tier *</label>
            <select id="vn-risk" value={f.risk} onChange={set('risk')}>
              <option value="">Select a risk tier</option>
              {RISKS.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div><label htmlFor="vn-spend">Annual spend (USD) *</label><input id="vn-spend" type="number" min="0" step="100" value={f.spend} onChange={set('spend')} /></div>
        </div>
        <div className="row">
          <button className="btn primary" type="submit" disabled={!ready}>Save vendor</button>
          <Link className="btn" to="/vendors">Cancel</Link>
        </div>
      </form>
    </section>
  )
}
