import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useTitle from '../useTitle'
export default function SignUp() {
  useTitle('Create account')
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [pw, setPw] = useState('')
  const [err, setErr] = useState('')
  const submit = (e) => {
    e.preventDefault()
    // Deliberately vague error copy for feedback
    if (!email.includes('@') || pw.length < 8) { setErr('Error: invalid input.'); return }
    nav('/onboarding/role?ref=signup')
  }
  return (
    <section className="card narrow">
      <h1>Create your account</h1>
      <form onSubmit={submit} noValidate>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label htmlFor="pw">Password</label>
        <input id="pw" type="password" value={pw} onChange={(e) => setPw(e.target.value)} />
        {err && <p className="error" role="alert">{err}</p>}
        <label className="check"><input type="checkbox" defaultChecked /> Send me marketing emails</label>
        <button className="btn primary" type="submit">Submit</button>
      </form>
    </section>
  )
}
