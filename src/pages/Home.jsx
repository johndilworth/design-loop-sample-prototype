import { Link } from 'react-router-dom'
import useTitle from '../useTitle'
export default function Home() {
  useTitle('Home')
  return (
    <section>
      <h1>Transform your org with AI</h1>
      <p className="lede">Northwind AI Ops helps teams leverage synergistic AI enablement across the enterprise value chain.</p>
      <div className="row">
        <Link className="btn primary" to="/signup">Get started</Link>
        <Link className="btn" to="/vendors">Vendors</Link>
      </div>
    </section>
  )
}
