type Props = { onLogin: () => void; onRegister: () => void }
export function LandingPage({ onLogin, onRegister }: Props) {
  return <main className="app-shell"><nav className="topbar"><strong className="brand">Finanças</strong><span className="status">Frontend inicial</span></nav>
    <section className="welcome"><div className="welcome-copy"><span className="eyebrow">GESTÃO SIMPLES E CLARA</span><h1>Seu dinheiro, organizado.</h1><p>Acompanhe receitas, compras parceladas e suas contas financeiras em um só lugar.</p>
      <div className="actions"><button type="button" onClick={onLogin}>Entrar</button><button type="button" className="secondary" onClick={onRegister}>Criar conta</button></div>
    </div><div className="summary-card" aria-label="Resumo financeiro"><span>Resumo mensal</span><strong>R$ 4.280,00</strong><small>Saldo disponível</small></div></section></main>
}
