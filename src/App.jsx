import { Routes, Route, Link, NavLink, Navigate, useLocation } from 'react-router-dom'
import Home from './pages/Home.jsx'
import SignUp from './pages/SignUp.jsx'
import OnboardingRole from './pages/OnboardingRole.jsx'
import OnboardingGoals from './pages/OnboardingGoals.jsx'
import WorkspaceReady from './pages/WorkspaceReady.jsx'
import VendorList from './pages/VendorList.jsx'
import VendorDetail from './pages/VendorDetail.jsx'
import VendorNew from './pages/VendorNew.jsx'
import VendorReview from './pages/VendorReview.jsx'
import NotFound from './pages/NotFound.jsx'
import AsciiBackground from './components/AsciiBackground.jsx'
import logoUrl from './assets/logo.svg'

// Landing + signup/onboarding screens get vertically centred content (cycle-3: '/' added).
const CENTERED = /^\/($|signup|onboarding\/|workspace\/)/

export default function App() {
  const { pathname } = useLocation()
  const isHome = pathname === '/'
  return (
    <>
    {/* cycle-3 feedback: the animated ASCII background is home-only (cycle 2 had it on every screen). */}
    {isHome && <AsciiBackground />}
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <img src={logoUrl} alt="" width="36" height="36" className="brand-mark" />
          <span className="brand-word">Northwind <strong>AI Ops</strong></span>
        </Link>
        <nav aria-label="Primary">
          <NavLink to="/vendors">Vendors</NavLink>
          <NavLink to="/signup">Sign up</NavLink>
        </nav>
      </header>
      <main className={'content' + (CENTERED.test(pathname) ? ' centered' : '') + (isHome ? ' home' : '')}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/onboarding/role" element={<OnboardingRole />} />
          <Route path="/onboarding/goals" element={<OnboardingGoals />} />
          <Route path="/workspace/:workspaceId" element={<WorkspaceReady />} />
          {/* cycle-4 feedback: invite is part of the workspace-created screen now. */}
          <Route path="/workspace/:workspaceId/invite" element={<Navigate to=".." relative="path" replace />} />
          <Route path="/vendors" element={<VendorList />} />
          <Route path="/vendors/new" element={<VendorNew />} />
          <Route path="/vendors/:id" element={<VendorDetail />} />
          <Route path="/vendors/:id/review" element={<VendorReview />} />
          {/* cycle-3 feedback: the "Success!" screen is gone; Approve returns to the list with a toast. */}
          <Route path="/vendors/:id/approved" element={<Navigate to="/vendors" replace />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
    </>
  )
}
