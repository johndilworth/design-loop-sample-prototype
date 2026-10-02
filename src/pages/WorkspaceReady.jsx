import { useParams } from 'react-router-dom'
import useTitle from '../useTitle'
import InviteForm from '../components/InviteForm'
// cycle-4 feedback: "Workspace created" and "Invite teammates" are one screen (the separate
// /workspace/:id/invite step is gone and redirects here). Skip goes to the vendor list.
export default function WorkspaceReady() {
  useTitle('Workspace created')
  const { workspaceId } = useParams()
  return (
    <section className="card narrow">
      <h1>Workspace created</h1>
      <p>Your workspace <code>{workspaceId}</code> is ready. Invite your teammates now, or skip and do it later.</p>
      <InviteForm workspaceId={workspaceId} />
    </section>
  )
}
