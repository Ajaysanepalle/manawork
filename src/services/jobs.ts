import axios from 'axios'
import { sampleJobs } from '../data/sampleJobs'
import type { Job } from '../types/job'

export type JobFilters = {
  keyword: string
  location: string
  mode: 'all' | 'remote' | 'onsite'
  sort: 'newest' | 'salary'
}

type JobsResponse = {
  success: boolean
  data: { items: Job[]; total: number }
}

export type TrackedUser = {
  id: string
  email: string | null
  full_name: string | null
  picture_url: string | null
  signup_method: string
  google_linked: boolean
  last_login_at: string | null
  last_login_method: string | null
  last_login_ip: string | null
  created_at: string
}

export type JobDraft = {
  title: string
  company: string
  location: string
  mode: Job['mode']
  employment_type: string
  experience: string
  salary: string
  apply_url: string
  tags: string[]
  description: string
  responsibilities: string[]
  requirements: string[]
}

export async function getJobs(filters: JobFilters): Promise<{ jobs: Job[]; total: number; isPreview: boolean }> {
  try {
    const response = await axios.get<JobsResponse>('/api/v1/jobs', { params: { q: filters.keyword || undefined, location: filters.location || undefined, mode: filters.mode === 'all' ? undefined : filters.mode, sort: filters.sort } })
    return { jobs: response.data.data.items, total: response.data.data.total, isPreview: false }
  } catch {
    const keyword = filters.keyword.toLocaleLowerCase()
    const location = filters.location.toLocaleLowerCase()
    const jobs = sampleJobs.filter((job) => {
      const matchesKeyword = !keyword || [job.title, job.company, ...job.tags].some((value) => value.toLocaleLowerCase().includes(keyword))
      const matchesLocation = !location || job.location.toLocaleLowerCase().includes(location)
      const matchesMode = filters.mode === 'all' || job.mode === filters.mode || (filters.mode === 'remote' && job.mode === 'hybrid')
      return matchesKeyword && matchesLocation && matchesMode
    })
    if (filters.sort === 'salary') jobs.sort((first, second) => second.salaryValue - first.salaryValue)
    return { jobs, total: jobs.length, isPreview: true }
  }
}

export async function getJob(jobId: string): Promise<Job | null> {
  try {
    const response = await axios.get<{ success: boolean; data: { job: Job } }>(`/api/v1/jobs/${jobId}`)
    return response.data.data.job
  } catch {
    return sampleJobs.find((job) => job.id === jobId) ?? null
  }
}

export async function createAdminJob(payload: JobDraft) {
  const response = await axios.post<{ success: boolean; data: { job: Job } }>('/api/v1/admin/jobs', payload, { withCredentials: true })
  return response.data.data.job
}

export async function updateAdminJob(jobId: string, payload: JobDraft) {
  const response = await axios.put<{ success: boolean; data: { job: Job } }>(`/api/v1/admin/jobs/${jobId}`, payload, { withCredentials: true })
  return response.data.data.job
}

export async function deleteAdminJob(jobId: string) {
  await axios.delete(`/api/v1/admin/jobs/${jobId}`, { withCredentials: true })
}

export async function getAdminJobs() {
  const response = await axios.get<{ success: boolean; data: { items: Job[]; total: number } }>('/api/v1/admin/jobs', { withCredentials: true })
  return response.data.data
}

export async function getTrackedUsers() {
  const response = await axios.get<{ success: boolean; data: { items: TrackedUser[]; total: number } }>('/api/v1/admin/users', { withCredentials: true })
  return response.data.data
}
