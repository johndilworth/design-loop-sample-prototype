import { useCallback, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
import { setVendorStatus, findAnyVendor } from '../vendorState'
import ConfirmDialog from '../components/ConfirmDialog'
import NotFound from './NotFound'
export default function VendorReview() {
  const { id } = useParams()
  const v = findAnyVendor(id)
  const nav = useNavigate()
  const [checks, setChecks] = useState({ dpa: false, soc2: false, pii: false })
  const [confirming, setConfirming] = useState(false)
  const cancel = useCallback(() => setConfirming(false), [])
  useTitle(v ? `Review: ${v.name}` : 'Vendor not found')
  if (!v) return <NotFound />
  const flip = (k) => setChecks((c) => ({ ...c, [k]: !c[k] }))
  // cycle-3 feedback: no separate "Success!" screen; update status and return to the list with a toast.
  const finish = (status, message) => {
    setVendorStatus(v.id, status)
    nav('/vendors', { state: { toast: message } })
  }
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
        {/* Reject now asks for confirmation; Approve is green (cycle-3 feedback). */}
        <button className="btn danger" type="button" onClick={() => setConfirming(true)}>Reject</button>
        <button className="btn success" type="button" onClick={() => finish('Approved', `${v.name} was updated.`)}>Approve</button>
      </div>
      {confirming && (
        <ConfirmDialog title={`Reject ${v.name}?`} confirmLabel="Confirm reject" onCancel={cancel}
          onConfirm={() => finish('Rejected', `${v.name} was rejected.`)}>
          <p>The vendor will be marked as Rejected. You can review it again later.</p>
        </ConfirmDialog>
      )}
    </section>
  )
}
