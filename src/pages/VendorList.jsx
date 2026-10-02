import { useCallback, useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import useTitle from '../useTitle'
import { statusClass } from '../data'
import { withStatus, allVendors } from '../vendorState'
import Toast from '../components/Toast'
export default function VendorList() {
  useTitle('Vendors')
  const location = useLocation()
  const nav = useNavigate()
  // cycle-3 feedback: the review step returns here with a toast instead of a separate "Success!" screen.
  const [toast, setToast] = useState(() => location.state?.toast || '')
  useEffect(() => {
    // Clear the one-shot router state so Back/refresh doesn't show the toast again.
    if (location.state?.toast) nav(location.pathname, { replace: true, state: null })
  }, [location, nav])
  const dismiss = useCallback(() => setToast(''), [])
  const rows = allVendors().map(withStatus)
  return (
    <section>
      {/* cycle-4 feedback: option to add a new vendor (opens /vendors/new). */}
      <div className="page-head">
        <div>
          <h1>AI vendors</h1>
          <p className="muted">{rows.length} vendors · sorted by nothing in particular</p>
        </div>
        <Link className="btn primary" to="/vendors/new">Add vendor</Link>
      </div>
      <table className="table">
        <thead><tr><th>Name</th><th>Category</th><th>Risk</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {rows.map((v) => (
            <tr key={v.id}>
              <td>{v.name}</td><td>{v.category}</td>
              <td><span className={'pill ' + v.risk.toLowerCase()}>{v.risk}</span></td>
              <td><span className={'chip status ' + statusClass(v.status)}>{v.status}</span></td>
              <td><Link to={`/vendors/${v.id}`} aria-label={`View ${v.name}`}>View</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
      <Toast message={toast} onDismiss={dismiss} />
    </section>
  )
}
