import { Link, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
import { findVendor } from '../data'
export default function VendorApproved() {
  const { id } = useParams()
  const v = findVendor(id)
  useTitle('Vendor approved')
  return (
    <section className="card">
      <h1>Success!</h1>
      <p>The operation completed. {v ? v.name : 'The vendor'} status was updated.</p>
      <div className="row">
        <Link className="btn" to="/vendors">OK</Link>
      </div>
    </section>
  )
}
