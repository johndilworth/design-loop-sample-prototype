import { Link, useParams } from 'react-router-dom'
import useTitle from '../useTitle'
export default function WorkspaceReady() {
  useTitle('Workspace created')
  const { workspaceId } = useParams()
  return (
    <section className="card">
      <h1>Workspace created</h1>
      <p>Your workspace <code>{workspaceId}</code> has been provisioned successfully.</p>
      <ul className="checklist">
        <li>Invite teammates</li>
        <li>Connect a data source</li>
        <li>Review AI vendors</li>
      </ul>
      <div className="row">
        <Link className="btn primary" to="/vendors">Go to vendors</Link>
      </div>
    </section>
  )
}
