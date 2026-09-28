import { useState, type FormEvent } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, ArrowUpRight } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { authErrorMessage, login, signup } from '../services/auth'

type AuthPageProps = { mode?: 'login' | 'signup' }

type GoogleStatus = {
  success: boolean
  data: { configured: boolean }
}

function AuthBackdrop({ signupMode }: { signupMode: boolean }) {
  return <div className="auth-note"><span className="eyebrow eyebrow-light">YOUR NEXT CHAPTER</span><h1>{signupMode ? <>Make room for<br />what’s <em>next.</em></> : <>Good to have<br />you <em>back.</em></>}</h1><p>{signupMode ? 'Create your account and start finding a path that feels like yours.' : 'One small step closer to work that feels like yours.'}</p><span className="auth-telugu">మీ ప్రయాణం ఇక్కడ మొదలవుతుంది</span></div>
}

export function AuthPage({ mode = 'login' }: AuthPageProps) {
  const signupMode = mode === 'signup'
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  const providerStatus = useQuery({
    queryKey: ['google-auth-status'],
    queryFn: async () => (await fetch('/api/v1/auth/google/status')).json() as Promise<GoogleStatus>,
    retry: false,
    staleTime: 60_000,
  })
  const googleConfigured = providerStatus.data?.data.configured === true

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setPending(true)
    try {
      if (signupMode) await signup({ full_name: fullName, email, password })
      else await login({ identifier: email, password })
      await queryClient.invalidateQueries({ queryKey: ['current-user'] })
      navigate('/')
    } catch (submitError) {
      setError(authErrorMessage(submitError))
    } finally {
      setPending(false)
    }
  }

  return <main className="auth-page"><AuthBackdrop signupMode={signupMode} /><section className="auth-form-wrap"><div className="auth-form">
    <span className="eyebrow section-eyebrow">WELCOME TO MANAWORKS</span>
    <h2>{signupMode ? 'Create your account' : 'Sign in to continue'}</h2>
    <p className="auth-subtitle">{signupMode ? 'Sign up with Google or create an account with your email.' : 'Continue with Google or sign in with your email.'}</p>
    {googleConfigured ? <a className="google-button" href="https://manawork.onrender.com/api/v1/auth/google/start"><span className="google-g">G</span>{signupMode ? 'Sign up with Google' : 'Continue with Google'}<ArrowUpRight size={15} /></a> : <button className="google-button is-unavailable" disabled type="button"><span className="google-g">G</span>{providerStatus.isLoading ? 'Checking Google sign-in…' : 'Google sign-in is not configured'}</button>}
    <div className="or-divider"><span /><em>or</em><span /></div>
    <form onSubmit={(event) => void onSubmit(event)}>
      {signupMode && <label className="form-label">Full name<input autoComplete="name" onChange={(event) => setFullName(event.target.value)} required value={fullName} /></label>}
      <label className="form-label">Email<input autoComplete="email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} /></label>
      <label className="form-label">Password<input autoComplete={signupMode ? 'new-password' : 'current-password'} minLength={6} onChange={(event) => setPassword(event.target.value)} required type="password" value={password} /></label>
      {error && <p className="auth-feedback">{error}</p>}
      <button className="button button-primary auth-submit" disabled={pending} type="submit">{pending ? 'Please wait…' : signupMode ? <>Create account <ArrowRight size={15} /></> : <>Sign in <ArrowRight size={15} /></>}</button>
    </form>
    <p className="signup-prompt">{signupMode ? 'Already started?' : 'New to ManaWorks?'} <Link to={signupMode ? '/login' : '/signup'}>{signupMode ? 'Sign in' : 'Create an account'} <ArrowUpRight size={14} /></Link></p>
    <Link className="back-home" to="/">← Back to home</Link>
  </div></section></main>
}
