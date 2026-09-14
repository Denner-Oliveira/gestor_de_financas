import { useState, type SubmitEvent } from 'react'
import type { Account } from '../types/finance'
import { saveTransaction } from '../services/api'

type Props = { type: 'income' | 'expense'; accounts: Account[]; onClose: () => void; onSaved: () => void }

export function TransactionForm({ type, accounts, onClose, onSaved }: Props) {
  const [description, setDescription] = useState(''); const [category, setCategory] = useState('')
  const [value, setValue] = useState(''); const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState(accounts[0]?.id.toString() ?? '')
  const [installments, setInstallments] = useState('1'); const [error, setError] = useState(''); const [saving, setSaving] = useState(false)

  async function save(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError('')
    const payload = type === 'income'
      ? { descricao: description, categoria: category, valor: value, data: date, conta_id: Number(accountId) }
      : { descricao: description, categoria: category, valor_total: value, quantidade_parcelas: Number(installments), data_compra: date, conta_id: Number(accountId) }
    const response = await saveTransaction(type, payload)
    if (!response.ok) {
      const data = await response.json().catch(() => null) as { detail?: string } | null
      setError(data?.detail ?? 'Não foi possível salvar o lançamento.'); setSaving(false); return
    }
    onSaved()
  }

  return <div className="modal-backdrop" role="presentation"><form className="login-card account-form" onSubmit={save}>
    <div className="section-heading"><h2>{type === 'income' ? 'Nova receita' : 'Nova compra'}</h2><button type="button" className="link-button" onClick={onClose}>Fechar</button></div>
    <label>Descrição<input value={description} onChange={(event) => setDescription(event.target.value)} required /></label>
    <label>Categoria<input value={category} onChange={(event) => setCategory(event.target.value)} required /></label>
    <label>Valor<input type="number" min="0.01" step="0.01" value={value} onChange={(event) => setValue(event.target.value)} required /></label>
    <label>Data<input type="date" value={date} onChange={(event) => setDate(event.target.value)} required /></label>
    <label>Conta financeira<select value={accountId} onChange={(event) => setAccountId(event.target.value)} required><option value="" disabled>Selecione uma conta</option>{accounts.map((account) => <option value={account.id} key={account.id}>{account.nome} · {account.banco}</option>)}</select></label>
    {type === 'expense' && <label>Quantidade de parcelas<input type="number" min="1" max="120" value={installments} onChange={(event) => setInstallments(event.target.value)} required /></label>}
    {error && <p className="form-error">{error}</p>}
    <button type="submit" disabled={saving || accounts.length === 0}>{saving ? 'Salvando...' : 'Salvar lançamento'}</button>
    {accounts.length === 0 && <p className="form-error">Cadastre uma conta antes de criar um lançamento.</p>}
  </form></div>
}
