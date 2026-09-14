import { useState } from 'react'
import './App.css'
import { DashboardPage } from './pages/DashboardPage'
import { AuthPage } from './pages/AuthPage'
import { LandingPage } from './pages/LandingPage'

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem('access_token')))
  const [email, setEmail] = useState(localStorage.getItem('user_email') ?? '')
  const [authMode, setAuthMode] = useState<'login' | 'register' | null>(null)
  const [success, setSuccess] = useState('')

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_email')
    setAuthenticated(false)
    setAuthMode(null)
  }

  if (authenticated) return <DashboardPage email={email} onLogout={logout} />
  if (authMode) return <AuthPage registerMode={authMode === 'register'} success={success} onBack={() => setAuthMode(null)} onAuthenticated={(userEmail) => { setEmail(userEmail); setAuthenticated(true) }} onToggle={() => setAuthMode(authMode === 'register' ? 'login' : 'register')} onSuccess={(message) => { setSuccess(message); setAuthMode('login') }} />
  return <LandingPage onLogin={() => { setSuccess(''); setAuthMode('login') }} onRegister={() => { setSuccess(''); setAuthMode('register') }} />
}

export default App
