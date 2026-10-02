import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useTitle from '../useTitle'
import { loadOnboarding, saveOnboarding } from '../onboardingState'
const roles = ['Executive sponsor', 'Product / Design', 'Engineering', 'Operations', 'Other']
export default function OnboardingRole() {
  useTitle('Onboarding: role')
  const nav = useNavigate()
  const [role, setRole] = useState(() => loadOnboarding().role || '')
  // Single choice, so selecting a role saves it and advances immediately (no Next button).
  const pick = (r) => {
    setRole(r)
    saveOnboarding({ role: r })
    nav('/onboarding/goals')
  }
  return (
    <section className="card">
      {/* cycle-4 feedback: no "Step 1 of 2" label (only two steps); more direct heading. */}
      <h1>Select your role</h1>
      <div className="choices" role="radiogroup" aria-label="Role">
        {roles.map((r) => (
          <button key={r} type="button" role="radio" aria-checked={role === r} className={'choice' + (role === r ? ' on' : '')} onClick={() => pick(r)}>{r}</button>
        ))}
      </div>
    </section>
  )
}
