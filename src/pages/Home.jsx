import { Link } from 'react-router-dom'
import useTitle from '../useTitle'

const VALUE_PROPS = [
  { title: 'One queue for AI vendor reviews', body: 'Collect the DPA, SOC 2 report and risk tier for every AI tool, then approve or reject it with a clear record of who decided and why.' },
  { title: 'Workspaces built around your goals', body: 'Tell us what you want AI to do (support triage, document summaries, knowledge search) and start from a workspace set up for it.' },
  { title: 'Spend and risk side by side', body: 'See annual spend, risk tier and review status for each vendor, so finance and security start from the same page.' },
]

export default function Home() {
  useTitle('Home')
  return (
    <section className="landing">
      <div className="hero">
        <p className="eyebrow">AI operations for growing teams</p>
        <h1>Transform your org with AI</h1>
        <p className="lede">Northwind AI Ops is where your team decides which AI tools to trust, sets them up, and keeps an eye on what they cost.</p>
        <div className="row">
          <Link className="btn primary" to="/signup">Get started</Link>
          <Link className="btn" to="/vendors">Vendors</Link>
        </div>
      </div>
      <div className="value-props">
        {VALUE_PROPS.map((p, i) => (
          <article className="value-prop" key={p.title}>
            <span className="value-num" aria-hidden="true">0{i + 1}</span>
            <h2>{p.title}</h2>
            <p>{p.body}</p>
          </article>
        ))}
      </div>
      <div className="cta-band">
        <div>
          <h2>Ready to set up your workspace?</h2>
          <p>Create an account, pick your role and goals, and invite teammates when you&apos;re ready.</p>
        </div>
        {/* Accessible name differs from the hero CTA so role+name locators ("Get started", exact) stay unique;
            it still contains the visible text (WCAG 2.5.3 label-in-name). */}
        <Link className="btn primary" to="/signup" aria-label="Get started with Northwind AI Ops">Get started</Link>
      </div>
    </section>
  )
}
