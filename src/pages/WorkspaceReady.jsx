import { Link, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
export default function WorkspaceReady() {
  useTitle('Workspace created')
  const { workspaceId } = useParams()
  return (
    <section className="card">
      <h1>Workspace created</h1>
      <p>Your workspace <code>{workspaceId}</code> has been provisioned successfully.</p>
      <div className="row">
        <Link className="btn" to="/vendors">Go to vendors</Link>
        <Link className="btn primary" to={`/workspace/${workspaceId}/invite`}>Invite teammates</Link>
      </div>
    </section>
  )
}
