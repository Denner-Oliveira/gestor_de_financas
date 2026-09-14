import type { AccountType } from '../types/finance'

export const accountTypeLabels: Record<AccountType, string> = {
  cartao_credito: 'Cartão de crédito',
  cartao_debito: 'Cartão de débito',
  conta_corrente: 'Conta corrente',
  conta_poupanca: 'Conta poupança',
  dinheiro: 'Dinheiro',
}
