import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useTitle from '../useTitle'
const roles = ['Executive sponsor', 'Product / design', 'Engineering', 'Operations', 'Other']
export default function OnboardingRole() {
  useTitle('Onboarding: role')
  const nav = useNavigate()
  const [role, setRole] = useState('')
  return (
    <section className="card">
      <p className="muted">Step 1</p>
      <h1>What's your role?</h1>
      <div className="choices" role="radiogroup" aria-label="Role">
        {roles.map((r) => (
          <button key={r} type="button" role="radio" aria-checked={role === r} className={'choice' + (role === r ? ' on' : '')} onClick={() => setRole(r)}>{r}</button>
        ))}
      </div>
      <div className="row">
        <button className="btn primary" type="button" onClick={() => nav('/onboarding/goals')}>Next</button>
      </div>
    </section>
  )
}
