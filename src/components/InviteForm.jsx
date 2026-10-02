import { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'
import Toast from './Toast'

const EMAIL = /^[^\s@,]+@[^\s@,]+\.[^\s@,]+$/
// Comma-separated list -> trimmed, non-empty entries.
const parseEmails = (s) => s.split(',').map((x) => x.trim()).filter(Boolean)

// cycle-4 feedback: invite teammates inline (open field, comma-separated emails), "Invite" disabled until
// every entry looks like an email, and "Skip" instead of "Back" (goes to /vendors).
export default function InviteForm({ workspaceId }) {
  const [value, setValue] = useState('')
  const [toast, setToast] = useState('')
  const dismiss = useCallback(() => setToast(''), [])
  const emails = parseEmails(value)
  const invalid = emails.filter((e) => !EMAIL.test(e))
  const canInvite = emails.length > 0 && invalid.length === 0
  const submit = (e) => {
    e.preventDefault()
    if (!canInvite) return
    setToast(`Invites sent to ${emails.length} teammate${emails.length === 1 ? '' : 's'}.`)
    setValue('')
  }
  return (
    <form className="invite-form" onSubmit={submit} noValidate>
      <h2>Invite your team</h2>
      <label htmlFor="invite-emails">Invite teammates</label>
      <textarea id="invite-emails" rows={2} value={value} onChange={(e) => setValue(e.target.value)}
        placeholder="jordan@example.com, sam@example.com" aria-describedby="invite-help" />
      <p id="invite-help" className="help">Enter email addresses separated by commas. They&apos;ll get access to <code>{workspaceId}</code>.</p>
      {value.trim() && invalid.length > 0 && <p className="error">Check {invalid.length === 1 ? 'this address' : 'these addresses'}: {invalid.join(', ')}</p>}
      <div className="row">
        <button className="btn primary" type="submit" disabled={!canInvite}>Invite</button>
        <Link className="btn" to="/vendors">Skip</Link>
      </div>
      <Toast message={toast} onDismiss={dismiss} />
    </form>
  )
}
