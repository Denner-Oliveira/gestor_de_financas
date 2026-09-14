import { useState } from 'react'
import './App.css'
import { DashboardPage } from './pages/DashboardPage'
import { AuthPage } from './pages/AuthPage'
import { LandingPage } from './pages/LandingPage'

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem('access_token')))
  const [email, setEmail] = useState(localStorage.getItem('user_email') ?? '')
  const [authMode, setAuthMode] = useState<'login' | 'register' | null>(null)
  const [recoveryMode, setRecoveryMode] = useState(false)
  const resetToken = new URLSearchParams(window.location.search).get('reset_token') ?? undefined
  const [success, setSuccess] = useState('')

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_email')
    setAuthenticated(false)
    setAuthMode(null)
  }

  if (authenticated) return <DashboardPage email={email} onLogout={logout} />
  if (authMode || recoveryMode || resetToken) return <AuthPage registerMode={authMode === 'register'} recoveryMode={recoveryMode} resetToken={resetToken} success={success} onBack={() => { setAuthMode(null); setRecoveryMode(false) }} onAuthenticated={(userEmail) => { setEmail(userEmail); setAuthenticated(true) }} onToggle={() => { setRecoveryMode(false); setAuthMode(authMode === 'register' ? 'login' : 'register') }} onRecovery={() => { setAuthMode(null); setRecoveryMode(true) }} onSuccess={(message) => { setSuccess(message); setRecoveryMode(false); setAuthMode('login'); window.history.replaceState({}, '', window.location.pathname) }} />
  return <LandingPage onLogin={() => { setSuccess(''); setAuthMode('login') }} onRegister={() => { setSuccess(''); setAuthMode('register') }} />
}

export default App
