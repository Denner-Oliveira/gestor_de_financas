import type { Account, Expense, Income } from '../types/finance'

export const API_URL = 'http://127.0.0.1:8000'

function authHeaders(contentType = false): HeadersInit {
  const token = localStorage.getItem('access_token') ?? ''
  return contentType
    ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    : { Authorization: `Bearer ${token}` }
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  if (!response.ok) throw new Error('E-mail ou senha inválidos.')
  return response.json() as Promise<{ access_token: string; refresh_token: string }>
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

export async function fetchDashboard(year: number, month: number, accountId: string) {
  const filter = accountId ? `&conta_id=${accountId}` : ''
  const query = `ano=${year}&mes=${month}${filter}`
  const headers = authHeaders()
  const responses = await Promise.all([
    fetch(`${API_URL}/contas`, { headers }),
    fetch(`${API_URL}/receitas?${query}`, { headers }),
    fetch(`${API_URL}/compras?${query}`, { headers }),
  ])
  if (responses.some((response) => response.status === 401)) throw new Error('UNAUTHORIZED')
  if (responses.some((response) => !response.ok)) throw new Error('Não foi possível carregar os dados do dashboard.')
  return {
    accounts: await responses[0].json() as Account[],
    incomes: await responses[1].json() as Income[],
    expenses: await responses[2].json() as Expense[],
  }
}

export async function deleteAccount(id: number) {
  return fetch(`${API_URL}/contas/${id}`, { method: 'DELETE', headers: authHeaders() })
}

export async function saveAccount(account: { id?: number; nome: string; banco: string; tipo: string }) {
  return fetch(`${API_URL}/contas${account.id ? `/${account.id}` : ''}`, {
    method: account.id ? 'PATCH' : 'POST',
    headers: authHeaders(true),
    body: JSON.stringify({ nome: account.nome, banco: account.banco, tipo: account.tipo }),
  })
}

export async function saveTransaction(type: 'income' | 'expense', payload: object) {
  return fetch(`${API_URL}/${type === 'income' ? 'receitas' : 'compras'}`, {
    method: 'POST',
    headers: authHeaders(true),
    body: JSON.stringify(payload),
  })
}
