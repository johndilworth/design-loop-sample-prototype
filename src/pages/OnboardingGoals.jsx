import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useTitle from '../useTitle'
const goals = ['Automate support triage', 'Summarize documents', 'Vendor risk reviews', 'Forecasting', 'Code assistance', 'Knowledge search']
export default function OnboardingGoals() {
  useTitle('Onboarding: goals')
  const nav = useNavigate()
  const [picked, setPicked] = useState([])
  const toggle = (g) => setPicked((p) => (p.includes(g) ? p.filter((x) => x !== g) : [...p, g]))
  return (
    <section className="card">
      <p className="muted">Step 2 of 2</p>
      <h1>Pick your AI goals</h1>
      <p>Select all that apply. You can't change these later.</p>
      <div className="choices">
        {goals.map((g) => (
          <label key={g} className="choice"><input type="checkbox" checked={picked.includes(g)} onChange={() => toggle(g)} /> {g}</label>
        ))}
      </div>
      <div className="row">
        <button className="btn ghost" type="button" onClick={() => nav(-1)}>Back</button>
        <button className="btn primary" type="button" onClick={() => nav('/workspace/ws-7781')}>Create workspace</button>
      </div>
    </section>
  )
}
