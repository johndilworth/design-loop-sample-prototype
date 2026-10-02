import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useTitle from '../useTitle'
import { loadOnboarding, saveOnboarding } from '../onboardingState'
const goals = ['Automate support triage', 'Summarize documents', 'Vendor risk reviews', 'Forecasting', 'Code assistance', 'Knowledge search']
export default function OnboardingGoals() {
  useTitle('Onboarding: goals')
  const nav = useNavigate()
  const [picked, setPicked] = useState(() => loadOnboarding().goals || [])
  const toggle = (g) => setPicked((p) => {
    const next = p.includes(g) ? p.filter((x) => x !== g) : [...p, g]
    saveOnboarding({ goals: next })
    return next
  })
  return (
    <section className="card">
      <p className="step-label">Step 2 of 2</p>
      <h1>Pick your AI goals</h1>
      <p>Select all that apply. You can't change these later.</p>
      {/* Highlight-on-select tiles (same look as the role step), multi-select via aria-pressed. */}
      <div className="choices" role="group" aria-label="Goals">
        {goals.map((g) => {
          const on = picked.includes(g)
          return <button key={g} type="button" aria-pressed={on} className={'choice' + (on ? ' on' : '')} onClick={() => toggle(g)}>{g}</button>
        })}
      </div>
      {/* cycle-3 feedback: primary action first, on the left (reverses cycle 1/2 "move to the right"). */}
      <div className="row">
        <button className="btn primary" type="button" onClick={() => nav('/workspace/ws-7781')}>Create workspace</button>
        <button className="btn" type="button" onClick={() => nav('/onboarding/role')}>Back</button>
      </div>
    </section>
  )
}
