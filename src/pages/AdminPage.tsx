import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, Pencil, Trash2, X } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { adminLogin, authErrorMessage, getCurrentUser } from '../services/auth'
import { createAdminJob, deleteAdminJob, getAdminJobs, getTrackedUsers, updateAdminJob, type JobDraft } from '../services/jobs'
import type { Job } from '../types/job'

const emptyJob = {
  title: '',
  company: '',
  location: '',
  mode: 'onsite' as Job['mode'],
  employment_type: 'Full-time',
  experience: '',
  salary: '',
  apply_url: '',
  tags: '',
  description: '',
  responsibilities: '',
  requirements: '',
}

export function AdminPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const currentUser = useQuery({ queryKey: ['current-user'], queryFn: getCurrentUser, retry: false })
  const [username, setUsername] = useState('ajay')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  const [editingJob, setEditingJob] = useState<Job | null>(null)
  const [jobForm, setJobForm] = useState(emptyJob)
  const isAdmin = currentUser.data?.role === 'ADMIN'
  const jobsQuery = useQuery({ queryKey: ['admin-jobs'], queryFn: getAdminJobs, enabled: isAdmin })
  const usersQuery = useQuery({ queryKey: ['tracked-users'], queryFn: getTrackedUsers, enabled: isAdmin })
  const saveJob = useMutation({
    mutationFn: (payload: JobDraft) => editingJob ? updateAdminJob(editingJob.id, payload) : createAdminJob(payload),
    onSuccess: async () => {
      setEditingJob(null)
      setJobForm(emptyJob)
      await queryClient.invalidateQueries({ queryKey: ['admin-jobs'] })
      await queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
  const removeJob = useMutation({
    mutationFn: deleteAdminJob,
    onSuccess: async (_, deletedId) => {
      if (editingJob?.id === deletedId) {
        setEditingJob(null)
        setJobForm(emptyJob)
      }
      await queryClient.invalidateQueries({ queryKey: ['admin-jobs'] })
      await queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })

  const onLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setPending(true)
    try {
      await adminLogin({ username, password })
      await queryClient.invalidateQueries({ queryKey: ['current-user'] })
    } catch (loginError) {
      setError(authErrorMessage(loginError))
    } finally {
      setPending(false)
    }
  }

  const onPublish = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    saveJob.mutate({
      title: jobForm.title,
      company: jobForm.company,
      location: jobForm.location,
      mode: jobForm.mode,
      employment_type: jobForm.employment_type,
      experience: jobForm.experience,
      salary: jobForm.salary,
      apply_url: jobForm.apply_url,
      tags: jobForm.tags.split(',').map((tag) => tag.trim()).filter(Boolean),
      description: jobForm.description,
      responsibilities: jobForm.responsibilities.split('\n').map((item) => item.trim()).filter(Boolean),
      requirements: jobForm.requirements.split('\n').map((item) => item.trim()).filter(Boolean),
    })
  }

  const editJob = (job: Job) => {
    setEditingJob(job)
    setJobForm({
      title: job.title,
      company: job.company,
      location: job.location,
      mode: job.mode,
      employment_type: job.employmentType,
      experience: job.experience,
      salary: job.salary === 'Salary not listed' ? '' : job.salary,
      apply_url: job.applyUrl ?? '',
      tags: job.tags.join(', '),
      description: job.description,
      responsibilities: job.responsibilities.join('\n'),
      requirements: job.requirements.join('\n'),
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (currentUser.isLoading) return <main className="admin-page"><p>Checking admin access…</p></main>
  if (currentUser.data && !isAdmin) {
    return <main className="admin-page"><h1>This page is for admins</h1><p>Job-seeker accounts use a separate profile.</p><button className="button button-primary" onClick={() => navigate('/profile')} type="button">Go to your profile</button></main>
  }
  if (!isAdmin) {
    return <main className="single-auth-page"><form className="auth-form" onSubmit={(event) => void onLogin(event)}>
      <span className="eyebrow section-eyebrow">ADMIN</span>
      <h2>Sign in to post jobs</h2>
      <p className="auth-subtitle">This workspace is separate from job-seeker accounts.</p>
      <label className="form-label">Username<input autoComplete="username" onChange={(event) => setUsername(event.target.value)} required value={username} /></label>
      <label className="form-label">Password<input autoComplete="current-password" onChange={(event) => setPassword(event.target.value)} required type="password" value={password} /></label>
      {error && <p className="auth-feedback">{error}</p>}
      <button className="button button-primary auth-submit" disabled={pending} type="submit">{pending ? 'Signing in…' : <>Enter admin <ArrowRight size={15} /></>}</button>
      <Link className="back-home" to="/">← Back to home</Link>
    </form></main>
  }

  return <main className="admin-page">
    <span className="eyebrow section-eyebrow">ADMIN WORKSPACE</span>
    <h1>Post jobs for seekers</h1>
    <p>Roles you publish here appear immediately on the public jobs board.</p>
    <div className="admin-grid">
      <form className="admin-card" onSubmit={onPublish}>
        <h2>{editingJob ? 'Edit opportunity' : 'New opportunity'}</h2>
        <label className="form-label">Job title<input onChange={(event) => setJobForm((current) => ({ ...current, title: event.target.value }))} required value={jobForm.title} /></label>
        <label className="form-label">Company<input onChange={(event) => setJobForm((current) => ({ ...current, company: event.target.value }))} required value={jobForm.company} /></label>
        <label className="form-label">Location<input onChange={(event) => setJobForm((current) => ({ ...current, location: event.target.value }))} required value={jobForm.location} /></label>
        <label className="form-label">Work mode<select onChange={(event) => setJobForm((current) => ({ ...current, mode: event.target.value as typeof current.mode }))} value={jobForm.mode}><option value="onsite">On-site</option><option value="hybrid">Hybrid</option><option value="remote">Remote</option></select></label>
        <label className="form-label">Employment type<input onChange={(event) => setJobForm((current) => ({ ...current, employment_type: event.target.value }))} value={jobForm.employment_type} /></label>
        <label className="form-label">Experience<input onChange={(event) => setJobForm((current) => ({ ...current, experience: event.target.value }))} required value={jobForm.experience} /></label>
        <label className="form-label">Salary<input onChange={(event) => setJobForm((current) => ({ ...current, salary: event.target.value }))} value={jobForm.salary} /></label>
        <label className="form-label">Application URL<input onChange={(event) => setJobForm((current) => ({ ...current, apply_url: event.target.value }))} placeholder="https://company.com/careers/job" required type="url" value={jobForm.apply_url} /></label>
        <label className="form-label">Tags<input onChange={(event) => setJobForm((current) => ({ ...current, tags: event.target.value }))} placeholder="Python, React, SQL" value={jobForm.tags} /></label>
        <label className="form-label">Description<textarea minLength={10} onChange={(event) => setJobForm((current) => ({ ...current, description: event.target.value }))} required rows={4} value={jobForm.description} /></label>
        <label className="form-label">Responsibilities<textarea onChange={(event) => setJobForm((current) => ({ ...current, responsibilities: event.target.value }))} placeholder="One per line" rows={3} value={jobForm.responsibilities} /></label>
        <label className="form-label">Requirements<textarea onChange={(event) => setJobForm((current) => ({ ...current, requirements: event.target.value }))} placeholder="One per line" rows={3} value={jobForm.requirements} /></label>
        {saveJob.isError && <p className="auth-feedback">{authErrorMessage(saveJob.error)}</p>}
        {removeJob.isError && <p className="auth-feedback">{authErrorMessage(removeJob.error)}</p>}
        {saveJob.isSuccess && <p className="auth-feedback success">{editingJob ? 'Changes saved.' : 'Published. Seekers can see this role now.'}</p>}
        <button className="button button-primary auth-submit" disabled={saveJob.isPending} type="submit">{saveJob.isPending ? 'Saving…' : editingJob ? 'Save changes' : 'Publish job'}</button>
        {editingJob && <button className="button button-outline auth-submit" onClick={() => { setEditingJob(null); setJobForm(emptyJob); saveJob.reset() }} type="button"><X size={15} /> Cancel edit</button>}
      </form>
      <section className="admin-card">
        <h2>Your published roles</h2>
        <ul className="admin-list">{jobsQuery.data?.items.length ? jobsQuery.data.items.map((job) => <li key={job.id}><strong>{job.title}</strong><span>{job.company} · {job.location}</span><div className="admin-job-actions"><button aria-label={`Edit ${job.title}`} className="button button-outline" onClick={() => editJob(job)} type="button"><Pencil size={14} /> Edit</button><button aria-label={`Delete ${job.title}`} className="button button-outline admin-delete-button" disabled={removeJob.isPending} onClick={() => { if (window.confirm(`Delete “${job.title}”? This cannot be undone.`)) removeJob.mutate(job.id) }} type="button"><Trash2 size={14} /> Delete</button></div></li>) : <li>No jobs posted yet.</li>}</ul>
      </section>
      <section className="admin-card admin-users">
        <h2>User tracking</h2>
        <p>{usersQuery.data?.total ?? 0} job-seeker accounts stored in the database.</p>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead><tr><th>Name</th><th>Email</th><th>Signup</th><th>Last login</th><th>IP</th></tr></thead>
            <tbody>
              {usersQuery.data?.items.map((user) => <tr key={user.id}>
                <td>{user.full_name || '—'}</td>
                <td>{user.email}</td>
                <td>{user.signup_method}{user.google_linked ? ' · Google linked' : ''}</td>
                <td>{user.last_login_at ? `${user.last_login_method ?? ''} ${new Date(user.last_login_at).toLocaleString()}` : '—'}</td>
                <td>{user.last_login_ip || '—'}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
}
