import { Link } from 'react-router-dom'
import useTitle from '../useTitle'
import { vendors } from '../data'
export default function VendorList() {
  useTitle('Vendors')
  return (
    <section>
      <h1>AI vendors</h1>
      <p className="muted">{vendors.length} vendors · sorted by nothing in particular</p>
      <table className="table">
        <thead><tr><th>Name</th><th>Category</th><th>Risk</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {vendors.map((v) => (
            <tr key={v.id}>
              <td>{v.name}</td><td>{v.category}</td>
              <td><span className={'pill ' + v.risk.toLowerCase()}>{v.risk}</span></td>
              <td>{v.status}</td>
              <td><Link to={`/vendors/${v.id}`} aria-label={`View ${v.name}`}>View</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
