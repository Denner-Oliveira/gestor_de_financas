import type { Account, Expense, GeneralReport, Income } from '../types/finance'

export const API_URL = 'http://127.0.0.1:8000'

type TokenResponse = { access_token: string; refresh_token: string }

let refreshPromise: Promise<boolean> | null = null

function clearStoredTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return false

  if (!refreshPromise) {
    refreshPromise = (async () => {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      if (!response.ok) {
        clearStoredTokens()
        return false
      }
      const tokens = await response.json() as TokenResponse
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      return true
    })().finally(() => {
      refreshPromise = null
    })
  }

  return refreshPromise
}

async function apiFetch(
  input: RequestInfo | URL,
  init: RequestInit = {},
  retry = true,
): Promise<Response> {
  const headers = new Headers(init.headers)
  const accessToken = localStorage.getItem('access_token')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  const response = await fetch(input, { ...init, headers })
  if (response.status !== 401 || !retry) return response

  const refreshed = await refreshAccessToken()
  if (!refreshed) return response
  return apiFetch(input, init, false)
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  if (!response.ok) throw new Error('E-mail ou senha inválidos.')
  return response.json() as Promise<TokenResponse>
}

export async function register(email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/registrar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha: password }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => null) as { detail?: unknown } | null
    throw new Error(typeof data?.detail === 'string' ? data.detail : 'Não foi possível criar sua conta.')
  }
}

export async function updateUser(payload: {
    email?: string
    senha_atual: string
    nova_senha?: string
  }) {
    const response = await apiFetch(`${API_URL}/auth/me`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const data = await response.json().catch(() => null) as { detail?: string } | null
      throw new Error(data?.detail ?? 'Não foi possível atualizar o usuário.')
    }
    return response.json() as Promise<{ email: string }>
}

export async function requestPasswordReset(email: string) {
    const response = await fetch(`${API_URL}/auth/recuperar-senha`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    if (!response.ok) {
      const data = await response.json().catch(() => null) as { detail?: unknown } | null
      throw new Error(
        typeof data?.detail === 'string'
          ? data.detail
          : 'Não foi possível solicitar a recuperação.',
      )
    }
}

export async function resetPassword(token: string, password: string) {
    const response = await fetch(`${API_URL}/auth/redefinir-senha`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, nova_senha: password }),
    })
    if (!response.ok) {
      const data = await response.json().catch(() => null) as { detail?: string } | null
      throw new Error(data?.detail ?? 'Link inválido ou expirado.')
    }
}
export async function fetchDashboard(year: number, month: number, accountId: string) {
  const filter = accountId ? `&conta_id=${accountId}` : ''
  const query = `ano=${year}&mes=${month}${filter}`
  const responses = await Promise.all([
    apiFetch(`${API_URL}/contas`),
    apiFetch(`${API_URL}/receitas?${query}`),
    apiFetch(`${API_URL}/compras?${query}`),
  ])
  if (responses.some((response) => response.status === 401)) throw new Error('UNAUTHORIZED')
  if (responses.some((response) => !response.ok)) throw new Error('Não foi possível carregar os dados do dashboard.')
  return {
    accounts: await responses[0].json() as Account[],
    incomes: await responses[1].json() as Income[],
    expenses: await responses[2].json() as Expense[],
  }
}

export async function fetchGeneralReport(inicio: string, fim: string) {
  const query = new URLSearchParams({ inicio, fim })
  const response = await apiFetch(`${API_URL}/relatorios/geral?${query}`)
  if (response.status === 401) throw new Error('UNAUTHORIZED')
  if (!response.ok) {
    const data = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(data?.detail ?? 'Não foi possível carregar o relatório.')
  }
  return response.json() as Promise<GeneralReport>
}

export async function deleteAccount(id: number) {
  return apiFetch(`${API_URL}/contas/${id}`, { method: 'DELETE' })
}

export async function saveAccount(account: { id?: number; nome: string; banco: string; tipo: string }) {
  return apiFetch(`${API_URL}/contas${account.id ? `/${account.id}` : ''}`, {
    method: account.id ? 'PATCH' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome: account.nome, banco: account.banco, tipo: account.tipo }),
  })
}

export async function saveTransaction(type: 'income' | 'expense', payload: object) {
  return apiFetch(`${API_URL}/${type === 'income' ? 'receitas' : 'compras'}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function importTransactions(file: File) {
  const formData = new FormData()
  formData.append('arquivo', file)
  return apiFetch(`${API_URL}/importacoes/lancamentos`, {
    method: 'POST',
    body: formData,
  })
}

export async function downloadImportTemplate() {
  const response = await apiFetch(`${API_URL}/importacoes/modelo`)
  if (!response.ok) throw new Error('Não foi possível baixar o modelo.')
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'modelo-lancamentos.xlsx'
  link.click()
  URL.revokeObjectURL(url)
}

export async function updateTransaction(
  type: 'income' | 'expense',
  id: number,
  payload: object,
) {
  return apiFetch(`${API_URL}/${type === 'income' ? 'receitas' : 'compras'}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function deleteTransaction(type: 'income' | 'expense', id: number) {
  return apiFetch(`${API_URL}/${type === 'income' ? 'receitas' : 'compras'}/${id}`, {
    method: 'DELETE',
  })
}
