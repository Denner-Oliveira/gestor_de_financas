import { useState, type SubmitEvent } from 'react'
import type { Account, Expense, Income } from '../types/finance'
import { saveTransaction, updateTransaction } from '../services/api'

type Props = {
  type: 'income' | 'expense'
  accounts: Account[]
  transaction?: Income | Expense
  onClose: () => void
  onSaved: () => void
}

export function TransactionForm({ type, accounts, transaction, onClose, onSaved }: Props) {
  const income = type === 'income' && transaction ? transaction as Income : undefined
  const expense = type === 'expense' && transaction ? transaction as Expense : undefined
  const [description, setDescription] = useState(income?.descricao ?? expense?.descricao ?? '')
  const [category, setCategory] = useState(income?.categoria ?? expense?.categoria ?? '')
  const [value, setValue] = useState(income?.valor ?? expense?.valor_total ?? '')
  const [date, setDate] = useState(income?.data ?? expense?.data_compra ?? new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState((income?.conta_id ?? expense?.conta_id ?? accounts[0]?.id)?.toString() ?? '')
  const [installments, setInstallments] = useState(expense?.parcelas.length.toString() ?? '1')
  const [error, setError] = useState(''); const [saving, setSaving] = useState(false)
  const editing = transaction !== undefined

  async function save(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError('')
    const payload = type === 'income'
      ? { descricao: description, categoria: category, valor: value, data: date, conta_id: Number(accountId) }
      : { descricao: description, categoria: category, valor_total: value, quantidade_parcelas: Number(installments), data_compra: date, conta_id: Number(accountId) }
    const response = editing
      ? await updateTransaction(type, transaction.id, payload)
      : await saveTransaction(type, payload)
    if (!response.ok) {
      const data = await response.json().catch(() => null) as { detail?: string } | null
      setError(data?.detail ?? 'Não foi possível salvar o lançamento.'); setSaving(false); return
    }
    onSaved()
  }

  return <div className="modal-backdrop" role="presentation"><form className="login-card account-form" onSubmit={save}>
    <div className="section-heading"><h2>{editing ? 'Editar' : 'Nova'} {type === 'income' ? 'receita' : 'compra'}</h2><button type="button" className="link-button" onClick={onClose}>Fechar</button></div>
    <label>Descrição<input value={description} onChange={(event) => setDescription(event.target.value)} required /></label>
    <label>Categoria<input value={category} onChange={(event) => setCategory(event.target.value)} required /></label>
    <label>Valor<input type="number" min="0.01" step="0.01" value={value} onChange={(event) => setValue(event.target.value)} required /></label>
    <label>Data<input type="date" value={date} onChange={(event) => setDate(event.target.value)} required /></label>
    <label>Conta financeira<select value={accountId} onChange={(event) => setAccountId(event.target.value)} required><option value="" disabled>Selecione uma conta</option>{accounts.map((account) => <option value={account.id} key={account.id}>{account.nome} · {account.banco}</option>)}</select></label>
    {type === 'expense' && <label>Quantidade de parcelas<input type="number" min="1" max="120" value={installments} onChange={(event) => setInstallments(event.target.value)} required /></label>}
    {error && <p className="form-error">{error}</p>}
    <button type="submit" disabled={saving || accounts.length === 0}>{saving ? 'Salvando...' : editing ? 'Salvar alterações' : 'Salvar lançamento'}</button>
    {accounts.length === 0 && <p className="form-error">Cadastre uma conta antes de criar um lançamento.</p>}
  </form></div>
}
