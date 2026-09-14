export function formatCurrency(value: number) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function monthLabel(year: number, month: number) {
  return new Date(year, month - 1, 1).toLocaleDateString('pt-BR', {
    month: 'long',
    year: 'numeric',
  })
}

export function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR')
}

export function isAccountType(value: string): value is import('../types/finance').AccountType {
  return ['cartao_credito', 'cartao_debito', 'conta_corrente', 'conta_poupanca', 'dinheiro'].includes(value)
}
