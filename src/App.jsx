import { Routes, Route, Link, NavLink, useLocation } from 'react-router-dom'
import Home from './pages/Home.jsx'
import SignUp from './pages/SignUp.jsx'
import OnboardingRole from './pages/OnboardingRole.jsx'
import OnboardingGoals from './pages/OnboardingGoals.jsx'
import WorkspaceReady from './pages/WorkspaceReady.jsx'
import InviteTeammates from './pages/InviteTeammates.jsx'
import VendorList from './pages/VendorList.jsx'
import VendorDetail from './pages/VendorDetail.jsx'
import VendorReview from './pages/VendorReview.jsx'
import VendorApproved from './pages/VendorApproved.jsx'
import NotFound from './pages/NotFound.jsx'

// Signup/onboarding screens get a vertically centred card.
const CENTERED = /^\/(signup|onboarding\/|workspace\/)/

export default function App() {
  const { pathname } = useLocation()
  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">Northwind AI Ops</Link>
        <nav aria-label="Primary">
          <NavLink to="/vendors">Vendors</NavLink>
          <NavLink to="/signup">Sign up</NavLink>
        </nav>
      </header>
      <main className={'content' + (CENTERED.test(pathname) ? ' centered' : '')}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/onboarding/role" element={<OnboardingRole />} />
          <Route path="/onboarding/goals" element={<OnboardingGoals />} />
          <Route path="/workspace/:workspaceId" element={<WorkspaceReady />} />
          <Route path="/workspace/:workspaceId/invite" element={<InviteTeammates />} />
          <Route path="/vendors" element={<VendorList />} />
          <Route path="/vendors/:id" element={<VendorDetail />} />
          <Route path="/vendors/:id/review" element={<VendorReview />} />
          <Route path="/vendors/:id/approved" element={<VendorApproved />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  )
}
