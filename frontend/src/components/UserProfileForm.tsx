import { useState, type SubmitEvent } from 'react'
import { updateUser } from '../services/api'

type Props = {
  email: string
  onClose: () => void
  onSaved: (email: string) => void
}

export function UserProfileForm({ email, onClose, onSaved }: Props) {
  const [newEmail, setNewEmail] = useState(email)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function submit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const data = await updateUser({
        email: newEmail !== email ? newEmail : undefined,
        senha_atual: currentPassword,
        nova_senha: newPassword || undefined,
      })
      localStorage.setItem('user_email', data.email)
      onSaved(data.email)
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Não foi possível atualizar.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <form className="login-card account-form" onSubmit={submit}>
        <div className="section-heading">
          <h2>Minha conta</h2>
          <button type="button" className="link-button" onClick={onClose}>Fechar</button>
        </div>
        <label>E-mail<input type="email" value={newEmail} onChange={(event) => setNewEmail(event.target.value)} required /></label>
        <label>Senha atual<input type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} minLength={8} required /></label>
        <label>Nova senha <small>(deixe vazia para não alterar)</small><input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} minLength={8} /></label>
        {error && <p className="form-error">{error}</p>}
        <button type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Salvar alterações'}</button>
      </form>
    </div>
  )
}
