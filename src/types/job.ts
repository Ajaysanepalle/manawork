export type Job = {
  id: string
  title: string
  company: string
  companyMark: string
  companyTone: string
  location: string
  mode: 'remote' | 'hybrid' | 'onsite'
  employmentType: string
  experience: string
  salary: string
  salaryValue: number
  applyUrl?: string | null
  postedAt: string
  tags: string[]
  description: string
  responsibilities: string[]
  requirements: string[]
}