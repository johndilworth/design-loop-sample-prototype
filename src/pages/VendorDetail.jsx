import { Link, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
import { findVendor, vendors, formatUsd, totalSpend, statusClass } from '../data'
import { withStatus } from '../vendorState'
import NotFound from './NotFound'

// cycle-3 feedback: "sheet of paper" vendor record instead of a plain table, with an
// annual-spend dashboard graphic and Status / Risk shown as chips.
export default function VendorDetail() {
  const { id } = useParams()
  const v = withStatus(findVendor(id))
  useTitle(v ? `Vendor: ${v.name}` : 'Vendor not found')
  if (!v) return <NotFound />
  const total = totalSpend()
  const share = Math.round((v.spend / total) * 100)
  const max = Math.max(...vendors.map((x) => x.spend))
  return (
    <section className="sheet">
      <div className="sheet-head">
        <Link to="/vendors" className="back-link">← Back</Link>
        <p className="sheet-kicker">Vendor record · {v.id}</p>
        <h1>{v.name}</h1>
        <div className="chips">
          <span className={'chip status ' + statusClass(v.status)}><span className="chip-k">Status</span>{v.status}</span>
          {v.risk && <span className={'chip risk ' + v.risk.toLowerCase()}><span className="chip-k">Risk</span>{v.risk}</span>}
        </div>
      </div>
      <div className="sheet-body">
        <dl className="fields">
          <div><dt>Category</dt><dd>{v.category}</dd></div>
          <div><dt>Model / service</dt><dd>{v.model}</dd></div>
          <div><dt>Business owner</dt><dd>{v.owner}</dd></div>
          <div><dt>Risk tier</dt><dd>{v.risk}</dd></div>
        </dl>
        <div className="spend-panel" aria-labelledby="spend-h">
          <h2 id="spend-h" className="panel-label">Annual spend</h2>
          <p className="spend-big">{formatUsd(v.spend)}<span> / yr</span></p>
          <div className="meter" role="img" aria-label={`${share}% of total AI vendor spend`}>
            <div className="meter-fill" style={{ width: `${share}%` }} />
          </div>
          <p className="spend-note">{share}% of total AI vendor spend ({formatUsd(total)} across {vendors.length} vendors)</p>
          <ul className="spend-bars" aria-label="Annual spend by vendor">
            {vendors.map((x) => (
              <li key={x.id} className={x.id === v.id ? 'current' : ''}>
                <span className="bar-name">{x.name}</span>
                <span className="bar-track"><span className="bar-fill" style={{ width: `${(x.spend / max) * 100}%` }} /></span>
                <span className="bar-val">{formatUsd(x.spend)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="row">
        <Link className="btn primary" to={`/vendors/${v.id}/review`}>Proceed</Link>
      </div>
    </section>
  )
}
