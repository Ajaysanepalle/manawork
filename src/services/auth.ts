import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1', withCredentials: true })

type AuthResult = {
  success: boolean
  message?: string
  data: { user?: AuthUser; csrf_token?: string }
}

export type AuthUser = {
  id: string
  email: string | null
  username: string | null
  phone: string | null
  full_name: string | null
  picture_url: string | null
  role: string
  signup_method: string
  last_login_at: string | null
  last_login_method: string | null
}

async function postAuth(path: string, payload: object): Promise<AuthResult> {
  const csrf = await api.get<AuthResult>('/auth/csrf')
  return (await api.post<AuthResult>(`/auth/${path}`, payload, {
    headers: { 'X-CSRF-Token': csrf.data.data.csrf_token },
  })).data
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  try {
    const response = await api.get<AuthResult>('/auth/me')
    return response.data.data.user ?? null
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      try {
        await postAuth('refresh', {})
        const response = await api.get<AuthResult>('/auth/me')
        return response.data.data.user ?? null
      } catch {
        return null
      }
    }
    throw error
  }
}

export async function signup(payload: { full_name: string; email: string; password: string }) {
  return postAuth('signup', payload)
}

export async function login(payload: { identifier: string; password: string }) {
  return postAuth('login', payload)
}

export async function adminLogin(payload: { username: string; password: string }) {
  return postAuth('admin/login', payload)
}

export async function logout() {
  return postAuth('logout', {})
}

export function authErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail?.message ?? error.response?.data?.message ?? 'Something went wrong. Please try again.'
  }
  return 'Something went wrong. Please try again.'
}
