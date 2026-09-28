import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Link, Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowDownUp, ArrowRight, ArrowUpRight, Bookmark, BriefcaseBusiness, Check, ChevronDown, Clock3, Code2, MapPin, Menu, Search, Sparkles, X } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { AdminPage } from './pages/AdminPage'
import { AuthPage } from './pages/AuthPages'
import { ProfilePage } from './pages/ProfilePage'
import { getCurrentUser, logout } from './services/auth'
import { getJob, getJobs, type JobFilters } from './services/jobs'
import type { Job } from './types/job'
import './manaworks.css'

function Header({ savedCount }: { savedCount: number }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const currentUser = useQuery({ queryKey: ['current-user'], queryFn: getCurrentUser, retry: false, staleTime: 60_000 })
  const signOut = async () => {
    try {
      await logout()
      await queryClient.invalidateQueries({ queryKey: ['current-user'] })
    } catch {
      await queryClient.setQueryData(['current-user'], null)
    }
  }
  return <header className="site-header">
    <Link aria-label="ManaWorks home" className="wordmark" to="/"><span className="brand-mark">m.</span><span>mana<span className="wordmark-light">works</span></span></Link>
    <button aria-expanded={menuOpen} aria-label={menuOpen ? 'Close navigation' : 'Open navigation'} className="icon-button menu-toggle" onClick={() => setMenuOpen(!menuOpen)} type="button">{menuOpen ? <X size={20} /> : <Menu size={20} />}</button>
    <nav aria-label="Main navigation" className={menuOpen ? 'main-nav is-open' : 'main-nav'}>
      <Link className="nav-link is-current" onClick={() => setMenuOpen(false)} to="/jobs">Find jobs</Link>
      <a className="nav-link" href="#career-tools" onClick={() => setMenuOpen(false)}>Career tools</a>
      <a className="nav-link" href="#roadmaps" onClick={() => setMenuOpen(false)}>Skill roadmaps</a>
      {currentUser.data?.role === 'ADMIN' ? <Link className="nav-link" onClick={() => setMenuOpen(false)} to="/admin">Admin</Link> : currentUser.data ? <Link className="nav-link" onClick={() => setMenuOpen(false)} to="/profile">Profile</Link> : null}
      {currentUser.data ? <button className="nav-link mobile-signin nav-action" onClick={() => { setMenuOpen(false); void signOut() }} type="button">Sign out</button> : <Link className="nav-link mobile-signin" onClick={() => setMenuOpen(false)} to="/login">Sign in</Link>}
    </nav>
    <div className="header-actions"><button className="button button-outline saved-jobs-button" onClick={() => { setMenuOpen(false); navigate('/saved') }} type="button"><Bookmark size={15} /> Saved <span className="saved-count">{savedCount}</span></button>{currentUser.data ? <button className="button button-outline header-signin" onClick={() => void signOut()} type="button">Sign out <ArrowUpRight size={15} /></button> : <Link className="button button-outline header-signin" to="/login">Sign in <ArrowUpRight size={15} /></Link>}</div>
  </header>
}

function JobCard({ job, index, isSaved, onSave }: { job: Job; index: number; isSaved: boolean; onSave: () => void }) {
  return <motion.article animate={{ opacity: 1, y: 0 }} className="job-card" initial={{ opacity: 0, y: 12 }} transition={{ delay: Math.min(index * 0.045, 0.22), duration: 0.35 }}>
    <div className="job-company-row"><div aria-hidden="true" className={`company-avatar ${job.companyTone}`}>{job.companyMark}</div><span className="posted-time"><Clock3 size={13} /> {job.postedAt}</span><button aria-label={`${isSaved ? 'Remove' : 'Save'} ${job.title} at ${job.company}`} aria-pressed={isSaved} className={isSaved ? 'icon-button save-button is-saved' : 'icon-button save-button'} onClick={onSave} type="button"><Bookmark fill={isSaved ? 'currentColor' : 'none'} size={18} /></button></div>
    <Link className="job-title-link" to={`/jobs/${job.id}`}><h3>{job.title}</h3></Link>
    <p className="company-name">{job.company}</p>
    <div className="job-facts"><span><MapPin size={14} />{job.location}</span><span><BriefcaseBusiness size={14} />{job.experience}</span></div>
    <div className="job-tags">{job.tags.slice(0, 3).map((tag) => <span className="skill-tag" key={tag}>{tag}</span>)}</div>
    <div className="job-card-footer"><span className="salary">{job.salary}</span><Link aria-label={`View ${job.title}`} className="card-arrow" to={`/jobs/${job.id}`}><ArrowUpRight size={17} /></Link></div>
  </motion.article>
}

function DiscoveryPage({ savedJobs, onToggleSaved }: { savedJobs: Job[]; onToggleSaved: (job: Job) => void }) {
  const [comingSoonOpen, setComingSoonOpen] = useState(false)
  const [keywordInput, setKeywordInput] = useState('')
  const [locationInput, setLocationInput] = useState('')
  const [filters, setFilters] = useState<JobFilters>({ keyword: '', location: '', mode: 'all', sort: 'newest' })
  const currentUser = useQuery({ queryKey: ['current-user'], queryFn: getCurrentUser, retry: false, staleTime: 60_000 })
  const jobsQuery = useQuery({ queryKey: ['jobs', filters], queryFn: () => getJobs(filters), enabled: Boolean(currentUser.data) })
  const jobs = jobsQuery.data?.jobs ?? []
  const featuredSkills = useMemo(() => ['Python', 'React', 'Data Analytics', 'Java', 'AI / ML', 'Cloud'], [])

  const applySearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFilters((current) => ({ ...current, keyword: keywordInput.trim(), location: locationInput.trim() }))
  }

  return <>
    <main>
      <section className="hero-section">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot" /> YOUR NEXT CHAPTER STARTS HERE</div>
          <h1>Find work that<br /><em>moves you forward.</em></h1>
          <p className="hero-description">Good jobs. Useful skills. A little guidance when you need it.<br className="desktop-break" /> All in one place, made for your journey.</p>
          <form className="search-panel" onSubmit={applySearch}>
            <label className="search-field"><Search aria-hidden="true" size={19} /><span className="sr-only">Job title, skill, or company</span><input onChange={(event) => setKeywordInput(event.target.value)} placeholder="Job title, skill, or company" value={keywordInput} /></label>
            <span aria-hidden="true" className="search-divider" />
            <label className="search-field location-field"><MapPin aria-hidden="true" size={19} /><span className="sr-only">City or state</span><input onChange={(event) => setLocationInput(event.target.value)} placeholder="City or state" value={locationInput} /></label>
            <button className="button button-primary search-submit" type="submit">Search jobs <ArrowRight size={17} /></button>
          </form>
          <div className="popular-searches"><span>Popular:</span> {['Software Engineer', 'Data Analyst', 'Internship'].map((term) => <button key={term} onClick={() => { setKeywordInput(term); setFilters((current) => ({ ...current, keyword: term })) }} type="button">{term}</button>)}</div>
        </div>
        <div className="hero-visual"><img alt="Colleagues sharing ideas in a bright workspace" className="hero-photo" src="https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=1050&q=85" /><div className="hero-photo-wash" /><div className="hero-note"><span className="note-icon"><Sparkles size={16} /></span><span><strong>Your next step, clearer.</strong><small>Jobs that fit your direction</small></span></div><div className="hero-caption"><span>CAREERS, WITH A LITTLE MORE CLARITY</span><span>01 / 03</span></div></div>
        <div aria-hidden="true" className="hero-index">01</div>
      </section>
      <section aria-label="ManaWorks career support" className="trust-strip"><span className="trust-label">BUILT FOR WHAT'S NEXT</span><span><Check size={15} /> Fresh opportunities</span><span><Check size={15} /> Skills that travel</span><span><Check size={15} /> Guidance in Telugu + English</span><span className="trust-script">mee career. mee pace.</span></section>
      <section className="jobs-section page-section" id="jobs">
        <div className="section-heading-row"><div><div className="eyebrow section-eyebrow">A GOOD PLACE TO BEGIN</div><h2>Opportunities worth<br className="mobile-break" /> a closer look<span className="heading-period">.</span></h2></div><Link className="text-link" to="/jobs">Explore all jobs <ArrowRight size={16} /></Link></div>
        <div className="filter-row"><div aria-label="Work arrangement" className="filter-tabs">{(['all', 'remote', 'onsite'] as const).map((mode) => <button aria-pressed={filters.mode === mode} className={filters.mode === mode ? 'filter-tab is-active' : 'filter-tab'} key={mode} onClick={() => setFilters((current) => ({ ...current, mode }))} type="button">{mode === 'all' ? 'All jobs' : mode === 'remote' ? 'Remote' : 'On-site'}</button>)}</div><label className="sort-control"><ArrowDownUp size={15} /><span className="sr-only">Sort jobs</span><select onChange={(event) => setFilters((current) => ({ ...current, sort: event.target.value as JobFilters['sort'] }))} value={filters.sort}><option value="newest">Most recent</option><option value="salary">Salary: high to low</option></select><ChevronDown size={14} /></label></div>
        {currentUser.isLoading ? <div className="jobs-access-prompt" role="status">Checking your sign-in…</div> : !currentUser.data ? <div className="jobs-access-prompt"><h3>Sign in to view job postings</h3><p>Sign in or create an account to explore available roles.</p><Link className="button button-primary" to="/login">Sign in to continue <ArrowRight size={16} /></Link></div> : <>{jobsQuery.data?.isPreview && <div className="preview-note" role="status">Preview roles shown while the live jobs service is being connected.</div>}{jobsQuery.isLoading ? <div aria-label="Loading jobs" className="jobs-grid">{[1, 2, 3].map((item) => <div className="job-skeleton" key={item} />)}</div> : jobs.length ? <div className="jobs-grid">{jobs.slice(0, 6).map((job, index) => <JobCard index={index} isSaved={savedJobs.some((saved) => saved.id === job.id)} job={job} key={job.id} onSave={() => onToggleSaved(job)} />)}</div> : <div className="empty-state"><Search size={22} /><h3>No roles found just yet.</h3><p>Try a broader title or nearby city.</p><button className="text-link" onClick={() => { setKeywordInput(''); setLocationInput(''); setFilters({ keyword: '', location: '', mode: 'all', sort: 'newest' }) }} type="button">Clear search <ArrowRight size={15} /></button></div>}<div className="section-bottom"><span>{jobsQuery.data?.total ?? 0} roles to explore</span><Link className="button button-dark" to="/jobs">See all opportunities <ArrowRight size={16} /></Link></div></>}
      </section>
      <section className="career-band" id="career-tools"><div className="career-band-copy"><div className="eyebrow eyebrow-light">MORE THAN A JOB BOARD</div><h2>A career is built<br />one good move at a time.</h2><p>Make your next move with tools that meet you where you are, whether that's your first resume or your next big interview.</p><button className="button button-paper" onClick={() => setComingSoonOpen(true)} type="button">Explore career tools <ArrowRight size={16} /></button></div><div className="career-tools-grid"><button className="career-tool" onClick={() => setComingSoonOpen(true)} type="button"><span className="tool-symbol tool-coral"><Code2 size={20} /></span><span className="tool-number">01</span><strong>Know your resume</strong><small>Make every skill count.</small><ArrowUpRight className="tool-arrow" size={17} /></button><button className="career-tool" id="roadmaps" onClick={() => setComingSoonOpen(true)} type="button"><span className="tool-symbol tool-lime"><ArrowUpRight size={20} /></span><span className="tool-number">02</span><strong>Find your next skill</strong><small>A roadmap with a reason.</small><ArrowUpRight className="tool-arrow" size={17} /></button><button className="career-tool" onClick={() => setComingSoonOpen(true)} type="button"><span className="tool-symbol tool-sky"><Sparkles size={20} /></span><span className="tool-number">03</span><strong>Talk it through</strong><small>Career guidance in your language.</small><ArrowUpRight className="tool-arrow" size={17} /></button></div></section>
      <section className="skills-section page-section"><div className="skills-heading"><div><div className="eyebrow section-eyebrow">SKILLS THAT OPEN DOORS</div><h2>Start with what<br />you want to learn<span className="heading-period">.</span></h2></div><p>Explore the skills employers are looking for, then find a path that feels right for you.</p></div><div className="skills-list">{featuredSkills.map((skill, index) => <Link key={skill} to={`/jobs?skill=${encodeURIComponent(skill)}`}><span className="skill-index">0{index + 1}</span><span>{skill}</span><ArrowUpRight size={16} /></Link>)}</div></section>
    </main>
    <Footer />
    {comingSoonOpen && <div className="coming-soon-backdrop" onClick={() => setComingSoonOpen(false)}><section aria-labelledby="coming-soon-title" aria-modal="true" className="coming-soon-dialog" onClick={(event) => event.stopPropagation()} onKeyDown={(event) => { if (event.key === 'Escape') setComingSoonOpen(false) }} role="dialog"><button aria-label="Close" autoFocus className="icon-button coming-soon-close" onClick={() => setComingSoonOpen(false)} type="button"><X size={18} /></button><span className="coming-soon-icon"><Sparkles size={22} /></span><span className="eyebrow section-eyebrow">IN THE WORKS</span><h2 id="coming-soon-title">Coming soon</h2><p>We’re getting these career tools ready. Check back soon for a little more help with your next move.</p><button className="button button-primary" onClick={() => setComingSoonOpen(false)} type="button">Got it <ArrowRight size={15} /></button></section></div>}
  </>
}

function JobDetailPage({ savedJobIds, onToggleSaved }: { savedJobIds: string[]; onToggleSaved: (job: Job) => void }) {
  const { jobId } = useParams()
  const currentUser = useQuery({ queryKey: ['current-user'], queryFn: getCurrentUser, retry: false, staleTime: 60_000 })
  const query = useQuery({ queryKey: ['jobs', 'detail', jobId], queryFn: () => getJob(jobId ?? ''), enabled: Boolean(jobId && currentUser.data) })
  const job = query.data
  if (currentUser.isLoading) return <main className="detail-loading">Checking your sign-in…</main>
  if (!currentUser.data) return <Navigate replace to="/login" />
  if (query.isLoading) return <main className="detail-loading">Loading opportunity…</main>
  if (!job) return <main className="detail-loading"><h1>This role has moved on.</h1><Link className="text-link" to="/jobs">Browse open roles <ArrowRight size={16} /></Link></main>
  const isSaved = savedJobIds.includes(job.id)
  return <main className="detail-page"><Link className="back-link" to="/jobs">← Back to opportunities</Link><div className="detail-layout"><article className="detail-main"><div className="detail-company"><div className={`company-avatar avatar-large ${job.companyTone}`}>{job.companyMark}</div><span>{job.company}</span></div><h1>{job.title}</h1><div className="detail-facts"><span><MapPin size={16} />{job.location}</span><span><BriefcaseBusiness size={16} />{job.experience}</span><span><Clock3 size={16} />{job.postedAt}</span></div><div className="detail-tags">{job.tags.map((tag) => <span className="skill-tag" key={tag}>{tag}</span>)}</div><section className="detail-content"><h2>About the role</h2><p>{job.description}</p><h2>What you’ll do</h2><ul>{job.responsibilities.map((item) => <li key={item}>{item}</li>)}</ul><h2>What you’ll bring</h2><ul>{job.requirements.map((item) => <li key={item}>{item}</li>)}</ul></section></article><aside className="apply-panel"><span className="eyebrow section-eyebrow">THE DETAILS</span><strong className="detail-salary">{job.salary}</strong><span className="detail-mode">{job.mode === 'remote' ? 'Remote friendly' : job.mode === 'hybrid' ? 'Hybrid' : 'On-site'} · {job.employmentType}</span><button className="button button-primary apply-button" disabled={!job.applyUrl} onClick={() => job.applyUrl && window.location.assign(job.applyUrl)} type="button">{job.applyUrl ? 'Apply for this role' : 'Application link unavailable'} <ArrowRight size={16} /></button><button className="button button-outline save-detail" onClick={() => onToggleSaved(job)} type="button"><Bookmark fill={isSaved ? 'currentColor' : 'none'} size={16} /> {isSaved ? 'Saved' : 'Save for later'}</button></aside></div></main>
}

function SavedJobsPage({ jobs, onToggleSaved }: { jobs: Job[]; onToggleSaved: (job: Job) => void }) {
  const currentUser = useQuery({ queryKey: ['current-user'], queryFn: getCurrentUser, retry: false, staleTime: 60_000 })
  if (currentUser.isLoading) return <main className="detail-loading">Checking your sign-in…</main>
  if (!currentUser.data) return <Navigate replace to="/login" />
  return <main className="saved-page page-section"><Link className="back-link" to="/jobs">← Back to opportunities</Link><div className="section-heading-row"><div><div className="eyebrow section-eyebrow">YOUR SHORTLIST</div><h1>Saved jobs<span className="heading-period">.</span></h1></div><span className="saved-page-count">{jobs.length} {jobs.length === 1 ? 'job' : 'jobs'}</span></div>{jobs.length ? <div className="jobs-grid">{jobs.map((job, index) => <JobCard index={index} isSaved job={job} key={job.id} onSave={() => onToggleSaved(job)} />)}</div> : <div className="empty-state"><Bookmark size={22} /><h3>No saved jobs yet.</h3><p>Save roles you want to come back to and they’ll appear here.</p><Link className="button button-primary" to="/jobs">Explore jobs <ArrowRight size={16} /></Link></div>}</main>
}

function Footer() {
  return <footer className="site-footer"><Link aria-label="ManaWorks home" className="wordmark footer-wordmark" to="/"><span className="brand-mark">m.</span><span>mana<span className="wordmark-light">works</span></span></Link><p>Made for your next chapter.</p><span className="footer-telugu">మన పని. మన భవిష్యత్తు.</span><span className="footer-copyright">© 2026 ManaWorks</span></footer>
}

function App() {
  const [savedJobs, setSavedJobs] = useState<Job[]>(() => {
    try {
      const stored = window.localStorage.getItem('manaworks-saved-jobs')
      return stored ? JSON.parse(stored) as Job[] : []
    } catch {
      return []
    }
  })

  useEffect(() => {
    try {
      window.localStorage.setItem('manaworks-saved-jobs', JSON.stringify(savedJobs))
    } catch {
      return
    }
  }, [savedJobs])

  const toggleSavedJob = (job: Job) => {
    setSavedJobs((current) => current.some((saved) => saved.id === job.id)
      ? current.filter((saved) => saved.id !== job.id)
      : [job, ...current])
  }

  return <div className="app-shell"><Header savedCount={savedJobs.length} /><Routes><Route element={<DiscoveryPage onToggleSaved={toggleSavedJob} savedJobs={savedJobs} />} path="/" /><Route element={<DiscoveryPage onToggleSaved={toggleSavedJob} savedJobs={savedJobs} />} path="/jobs" /><Route element={<SavedJobsPage jobs={savedJobs} onToggleSaved={toggleSavedJob} />} path="/saved" /><Route element={<JobDetailPage onToggleSaved={toggleSavedJob} savedJobIds={savedJobs.map((job) => job.id)} />} path="/jobs/:jobId" /><Route element={<AuthPage />} path="/login" /><Route element={<AuthPage mode="signup" />} path="/signup" /><Route element={<ProfilePage />} path="/profile" /><Route element={<AdminPage />} path="/admin" /><Route element={<DiscoveryPage onToggleSaved={toggleSavedJob} savedJobs={savedJobs} />} path="*" /></Routes></div>
}

export default App
