import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
import { findVendor } from '../data'
import NotFound from './NotFound'
export default function VendorReview() {
  const { id } = useParams()
  const v = findVendor(id)
  const nav = useNavigate()
  const [checks, setChecks] = useState({ dpa: false, soc2: false, pii: false })
  useTitle(v ? `Review: ${v.name}` : 'Vendor not found')
  if (!v) return <NotFound />
  const flip = (k) => setChecks((c) => ({ ...c, [k]: !c[k] }))
  return (
    <section className="card">
      <h1>Review {v.name}</h1>
      <p className="muted">Confirm the compliance items below. Unchecked items will be ignored.</p>
      <fieldset>
        <legend>Compliance checklist</legend>
        <label className="check"><input type="checkbox" checked={checks.dpa} onChange={() => flip('dpa')} /> DPA signed</label>
        <label className="check"><input type="checkbox" checked={checks.soc2} onChange={() => flip('soc2')} /> SOC 2 Type II on file</label>
        <label className="check"><input type="checkbox" checked={checks.pii} onChange={() => flip('pii')} /> No PII sent to model</label>
      </fieldset>
      <label htmlFor="notes">Notes</label>
      <textarea id="notes" rows={3} placeholder="Notes" />
      <div className="row">
        <button className="btn danger" type="button" onClick={() => nav('/vendors')}>Reject</button>
        <button className="btn danger" type="button" onClick={() => nav(`/vendors/${v.id}/approved`)}>Approve</button>
      </div>
    </section>
  )
}
