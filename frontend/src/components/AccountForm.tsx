import { useState, type SubmitEvent } from 'react'
import type { Account, AccountType } from '../types/finance'
import { saveAccount } from '../services/api'
import { isAccountType } from '../utils/format'
import { accountTypeLabels } from '../utils/account'

type Props = { account: Account | null; onClose: () => void; onSaved: () => void }

export function AccountForm({ account, onClose, onSaved }: Props) {
  const [name, setName] = useState(account?.nome ?? '')
  const [bank, setBank] = useState(account?.banco ?? '')
  const [type, setType] = useState<AccountType>(account?.tipo ?? 'conta_corrente')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function save(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError('')
    const response = await saveAccount({ id: account?.id, nome: name, banco: bank, tipo: type })
    if (!response.ok) {
      const data = await response.json().catch(() => null) as { detail?: string } | null
      setError(data?.detail ?? 'Não foi possível salvar a conta.'); setSaving(false); return
    }
    onSaved()
  }

  return <div className="modal-backdrop" role="presentation">
    <form className="login-card account-form" onSubmit={save}>
      <div className="section-heading"><h2>{account ? 'Editar conta' : 'Nova conta'}</h2><button type="button" className="link-button" onClick={onClose}>Fechar</button></div>
      <label>Nome<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
      <label>Banco ou instituição<input value={bank} onChange={(event) => setBank(event.target.value)} required /></label>
      <label>Tipo<select value={type} onChange={(event) => { if (isAccountType(event.target.value)) setType(event.target.value) }}>
        {Object.entries(accountTypeLabels).map(([value, label]) => <option value={value} key={value}>{label}</option>)}
      </select></label>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Salvar conta'}</button>
    </form>
  </div>
}
