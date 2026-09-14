import { useState, type SubmitEvent } from 'react'
import { login, register } from '../services/api'

type Props = { registerMode: boolean; success: string; onBack: () => void; onAuthenticated: (email: string) => void; onToggle: () => void; onSuccess: (message: string) => void }
export function AuthPage({ registerMode, success, onBack, onAuthenticated, onToggle, onSuccess }: Props) {
  const [email, setEmail] = useState(localStorage.getItem('user_email') ?? '')
  const [password, setPassword] = useState(''); const [confirmation, setConfirmation] = useState('')
  const [error, setError] = useState(''); const [loading, setLoading] = useState(false)
  async function submit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setLoading(true)
    try {
      if (registerMode) {
        if (password !== confirmation) { setError('As senhas não coincidem.'); return }
        await register(email, password); onSuccess('Cadastro realizado. Entre com seu e-mail e senha.')
      } else {
        const tokens = await login(email, password)
        localStorage.setItem('access_token', tokens.access_token); localStorage.setItem('refresh_token', tokens.refresh_token); localStorage.setItem('user_email', email)
        onAuthenticated(email)
      }
    } catch (submitError) { setError(submitError instanceof Error ? submitError.message : 'Não foi possível realizar a operação.') }
    finally { setLoading(false) }
  }
  return <main className="app-shell"><nav className="topbar"><strong className="brand">Finanças</strong><button type="button" className="link-button" onClick={onBack}>Voltar</button></nav>
    <section className="login-page"><form className="login-card" onSubmit={submit}><div><span className="eyebrow">{registerMode ? 'COMECE AGORA' : 'ACESSO SEGURO'}</span><h1>{registerMode ? 'Criar conta' : 'Entrar'}</h1></div>
      {!registerMode && success && <p className="form-success">{success}</p>}<label>E-mail<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
      <label>Senha<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required /></label>
      {registerMode && <label>Confirmar senha<input type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} minLength={8} required /></label>}
      {error && <p className="form-error">{error}</p>}<button type="submit" disabled={loading}>{loading ? (registerMode ? 'Criando conta...' : 'Entrando...') : (registerMode ? 'Criar conta' : 'Entrar')}</button>
      <button type="button" className="link-button" onClick={() => { setError(''); onToggle() }}>{registerMode ? 'Já tenho uma conta' : 'Ainda não tenho uma conta'}</button>
    </form></section></main>
}
