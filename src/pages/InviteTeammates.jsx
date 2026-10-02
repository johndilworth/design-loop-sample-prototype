import { Link, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
// Placeholder target for the "Invite teammates" CTA (cycle-1 feedback). Real invite flow TBD.
export default function InviteTeammates() {
  useTitle('Invite teammates')
  const { workspaceId } = useParams()
  return (
    <section className="card narrow">
      <h1>Invite teammates</h1>
      <p>Inviting teammates to <code>{workspaceId}</code> is coming soon. For now, share your workspace ID with colleagues so they can request access.</p>
      <div className="row">
        <Link className="btn" to={`/workspace/${workspaceId}`}>Back</Link>
      </div>
    </section>
  )
}
