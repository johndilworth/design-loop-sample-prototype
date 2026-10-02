import { Link, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
import { findVendor } from '../data'
import NotFound from './NotFound'
export default function VendorDetail() {
  const { id } = useParams()
  const v = findVendor(id)
  useTitle(v ? `Vendor: ${v.name}` : 'Vendor not found')
  if (!v) return <NotFound />
  return (
    <section className="card">
      <Link to="/vendors" className="muted">← Back</Link>
      <h1>{v.name}</h1>
      <dl className="facts">
        <dt>Category</dt><dd>{v.category}</dd>
        <dt>Model / service</dt><dd>{v.model}</dd>
        <dt>Risk tier</dt><dd>{v.risk}</dd>
        <dt>Annual spend</dt><dd>{v.spend}</dd>
        <dt>Business owner</dt><dd>{v.owner}</dd>
        <dt>Status</dt><dd>{v.status}</dd>
      </dl>
      <div className="row">
        <Link className="btn" to={`/vendors/${v.id}/review`}>Proceed</Link>
      </div>
    </section>
  )
}
