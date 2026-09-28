import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getCurrentUser } from '../services/auth'

export function ProfilePage() {
  const currentUser = useQuery({ queryKey: ['current-user'], queryFn: getCurrentUser, retry: false })
  const user = currentUser.data
  if (currentUser.isLoading) return <main className="profile-page"><p>Loading your profile…</p></main>
  if (!user) return <main className="profile-page"><h1>Sign in to see your profile</h1><Link className="button button-primary" to="/login">Sign in</Link></main>
  if (user.role === 'ADMIN') return <main className="profile-page"><h1>Admin workspace is separate</h1><p>Job posting and user tracking live in the admin page.</p><Link className="button button-primary" to="/admin">Open admin</Link></main>
  return <main className="profile-page">
    <span className="eyebrow section-eyebrow">YOUR PROFILE</span>
    <h1>{user.full_name || 'Your account'}</h1>
    <p>This is your job-seeker profile. Posted roles from ManaWorks admins appear on the jobs board.</p>
    <dl className="profile-facts">
      <div><dt>Email</dt><dd>{user.email}</dd></div>
      <div><dt>Signed up with</dt><dd>{user.signup_method === 'google' ? 'Google' : 'Email and password'}</dd></div>
      <div><dt>Last sign-in</dt><dd>{user.last_login_method ? `${user.last_login_method}${user.last_login_at ? ` · ${new Date(user.last_login_at).toLocaleString()}` : ''}` : 'Just now'}</dd></div>
    </dl>
    <Link className="button button-dark" to="/jobs">Browse jobs</Link>
  </main>
}
