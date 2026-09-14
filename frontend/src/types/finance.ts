export type AccountType =
  | 'cartao_credito'
  | 'cartao_debito'
  | 'conta_corrente'
  | 'conta_poupanca'
  | 'dinheiro'

export type Account = {
  id: number
  nome: string
  banco: string
  tipo: AccountType
  ativa: boolean
}

export type Income = {
  id: number
  descricao: string
  categoria: string
  valor: string
  data: string
  conta_id: number | null
}

export type Installment = {
  valor: string
  status: string
  data_vencimento: string
}

export type Expense = {
  id: number
  descricao: string
  categoria: string
  valor_total: string
  data_compra: string
  conta_id: number | null
  parcelas: Installment[]
}
