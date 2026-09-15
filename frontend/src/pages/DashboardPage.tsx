import { useCallback, useEffect, useMemo, useState } from 'react'
import type { Account, Expense, Income } from '../types/finance'
import { deleteAccount, deleteTransaction, fetchDashboard } from '../services/api'
import { formatCurrency, formatDate, monthLabel } from '../utils/format'
import { AccountForm } from '../components/AccountForm'
import { accountTypeLabels } from '../utils/account'
import { TransactionForm } from '../components/TransactionForm'
import { UserProfileForm } from '../components/UserProfileForm'
import { ImportTransactionsForm } from '../components/ImportTransactionsForm'

type Props = { email: string; onLogout: () => void; onReport: () => void }
export function DashboardPage({ email, onLogout, onReport }: Props) {
  const now = new Date(); const [year, setYear] = useState(now.getFullYear()); const [month, setMonth] = useState(now.getMonth() + 1)
  const [accounts, setAccounts] = useState<Account[]>([]); const [incomes, setIncomes] = useState<Income[]>([]); const [expenses, setExpenses] = useState<Expense[]>([])
  const [error, setError] = useState(''); const [accountForm, setAccountForm] = useState<Account | null | false>(false); const [transaction, setTransaction] = useState<'income' | 'expense' | null>(null); const [selected, setSelected] = useState(''); const [menu, setMenu] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [importOpen, setImportOpen] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState<{
    type: 'income' | 'expense'
    transaction: Income | Expense
  } | null>(null)
  const load = useCallback(async () => {
    if (!localStorage.getItem('access_token')) { onLogout(); return }
    try { const data = await fetchDashboard(year, month, selected); setAccounts(data.accounts); setIncomes(data.incomes); setExpenses(data.expenses) }
    catch (loadError) { if (loadError instanceof Error && loadError.message === 'UNAUTHORIZED') onLogout(); else setError(loadError instanceof Error ? loadError.message : 'Não foi possível carregar os dados.') }
  }, [month, onLogout, selected, year])
  useEffect(() => { void load() }, [load])
  const title = useMemo(() => monthLabel(year, month), [month, year])
  const monthKey = `${year}-${String(month).padStart(2, '0')}`
  const totalIncome = incomes.reduce((sum, item) => sum + Number(item.valor), 0)
  const totalExpense = expenses.reduce((sum, item) => sum + item.parcelas.filter((p) => p.data_vencimento.startsWith(monthKey)).reduce((s, p) => s + Number(p.valor), 0), 0)
  const reportByAccount = accounts.map((account) => {
    const income = incomes.filter((item) => item.conta_id === account.id).reduce((sum, item) => sum + Number(item.valor), 0)
    const expense = expenses.filter((item) => item.conta_id === account.id).reduce((sum, item) => sum + item.parcelas.filter((p) => p.data_vencimento.startsWith(monthKey)).reduce((partial, p) => partial + Number(p.valor), 0), 0)
    return { account, income, expense }
  }).filter((item) => item.income > 0 || item.expense > 0)
  const reportByCategory = expenses.reduce<Record<string, number>>((result, item) => {
    const total = item.parcelas.filter((p) => p.data_vencimento.startsWith(monthKey)).reduce((sum, p) => sum + Number(p.valor), 0)
    result[item.categoria] = (result[item.categoria] ?? 0) + total
    return result
  }, {})
  function changeMonth(offset: number) { const date = new Date(year, month - 1 + offset, 1); setYear(date.getFullYear()); setMonth(date.getMonth() + 1) }
  async function removeAccount(account: Account) {
    if (!window.confirm(`Excluir a conta "${account.nome}"?`)) return
    const response = await deleteAccount(account.id)
    if (!response.ok) { const data = await response.json().catch(() => null) as { detail?: string } | null; setError(data?.detail ?? 'Não foi possível excluir a conta.'); return }
    await load()
  }
  async function removeTransaction(type: 'income' | 'expense', id: number) {
    if (!window.confirm('Excluir esta movimentação?')) return
    const response = await deleteTransaction(type, id)
    if (!response.ok) {
      const data = await response.json().catch(() => null) as { detail?: string } | null
      setError(data?.detail ?? 'Não foi possível excluir a movimentação.')
      return
    }
    await load()
  }
  return <main className="app-shell dashboard-shell"><nav className="topbar dashboard-topbar"><strong className="brand">Finanças</strong><div className="app-tabs" role="tablist" aria-label="Navegação principal"><button type="button" className="app-tab active" role="tab" aria-selected="true">Visão geral</button><button type="button" className="app-tab" onClick={onReport}>Relatório geral</button></div><div className="dashboard-nav"><div className="user-menu"><button type="button" className="user-button" onClick={() => setMenu(!menu)}>{email || 'Minha conta'} <span aria-hidden="true">⌄</span></button>  {menu && <div className="dropdown-menu"><span>{email}</span><button type="button" onClick={() => { setProfileOpen(true); setMenu(false) }}>Minha conta</button><button type="button" onClick={onLogout}>Sair</button></div>}</div></div></nav>
    <section className="dashboard-content"><div className="dashboard-heading"><div><span className="eyebrow">VISÃO GERAL</span><h1>Seu mês financeiro</h1></div><div className="month-switcher"><button type="button" onClick={() => changeMonth(-1)} aria-label="Mês anterior">←</button><strong>{title}</strong><button type="button" onClick={() => changeMonth(1)} aria-label="Próximo mês">→</button></div></div>
      {error && <p className="form-error">{error}</p>}<div className="dashboard-grid"><article className="balance-card"><span>Saldo do mês</span><strong>{formatCurrency(totalIncome - totalExpense)}</strong><small>{totalIncome - totalExpense >= 0 ? 'Resultado positivo até agora' : 'Despesas acima das receitas'}</small></article><article className="metric-card"><span>Receitas</span><strong className="income">{formatCurrency(totalIncome)}</strong><small>{incomes.length} lançamento(s)</small></article><article className="metric-card"><span>Despesas</span><strong className="expense">{formatCurrency(totalExpense)}</strong><small>{expenses.length} compra(s)</small></article></div>
      <div className="quick-actions"><button type="button" onClick={() => setTransaction('income')}>+ Nova receita</button><button type="button" className="secondary" onClick={() => setTransaction('expense')}>+ Nova compra</button><button type="button" className="secondary" onClick={() => setImportOpen(true)}>Importar XLSX</button></div>
      <div className="dashboard-panels">
      <section className="movements-section"><div className="section-heading"><div><span className="eyebrow">LANÇAMENTOS</span><h2>Movimentações de {title}</h2></div><label className="account-filter">Conta<select value={selected} onChange={(event) => setSelected(event.target.value)}><option value="">Todas as contas</option>{accounts.map((a) => <option value={a.id} key={a.id}>{a.nome}</option>)}</select></label></div>
        <div className="movement-list">{incomes.map((income) => <article className="movement-item" key={`income-${income.id}`}><div className="movement-icon income-icon">+</div><div className="movement-details"><strong>{income.descricao}</strong><span>{income.categoria} · {formatDate(income.data)}</span></div><strong className="income">+ {formatCurrency(Number(income.valor))}</strong><div className="movement-actions"><button type="button" onClick={() => setEditingTransaction({ type: 'income', transaction: income })}>Editar</button><button type="button" className="danger-button" onClick={() => void removeTransaction('income', income.id)}>Excluir</button></div></article>)}{expenses.map((expense) => <article className="movement-item" key={`expense-${expense.id}`}><div className="movement-icon expense-icon">−</div><div className="movement-details"><strong>{expense.descricao}</strong><span>{expense.categoria} · parcela do mês</span></div><strong className="expense">− {formatCurrency(expense.parcelas.filter((p) => p.data_vencimento.startsWith(monthKey)).reduce((s, p) => s + Number(p.valor), 0))}</strong><div className="movement-actions"><button type="button" onClick={() => setEditingTransaction({ type: 'expense', transaction: expense })}>Editar</button><button type="button" className="danger-button" onClick={() => void removeTransaction('expense', expense.id)}>Excluir</button></div></article>)}{incomes.length === 0 && expenses.length === 0 && <p className="empty-state">Nenhuma movimentação encontrada neste mês.</p>}</div>
      </section><section className="accounts-section"><div className="section-heading"><div><span className="eyebrow">ORGANIZAÇÃO</span><h2>Contas financeiras</h2></div><button type="button" onClick={() => setAccountForm(null)}>+ Adicionar conta</button></div><div className="account-list">{accounts.map((account) => <article className="account-card" key={account.id}><div><strong>{account.nome}</strong><span>{account.banco} · {accountTypeLabels[account.tipo]}</span></div><div className="account-actions"><button type="button" onClick={() => setAccountForm(account)}>Editar</button><button type="button" className="danger-button" onClick={() => void removeAccount(account)}>Excluir</button></div></article>)}{accounts.length === 0 && <p className="empty-state">Nenhuma conta encontrada.</p>}</div></section>
      </div><section className="report-section"><div className="section-heading"><div><span className="eyebrow">RESUMO RÁPIDO</span><h2>Resumo de {title}</h2></div></div><div className="report-grid"><article className="report-card"><span>Saldo</span><strong className={totalIncome - totalExpense >= 0 ? 'income' : 'expense'}>{formatCurrency(totalIncome - totalExpense)}</strong><small>Receitas menos despesas</small></article><article className="report-card"><span>Maior categoria de despesa</span><strong>{Object.entries(reportByCategory).sort((a, b) => b[1] - a[1])[0]?.[0] ?? 'Nenhuma'}</strong><small>{Object.entries(reportByCategory).length} categoria(s)</small></article></div><div className="report-columns"><div><h3>Totais por conta</h3>{reportByAccount.map(({ account, income, expense }) => <div className="report-row" key={account.id}><span>{account.nome}</span><strong className={income - expense >= 0 ? 'income' : 'expense'}>{formatCurrency(income - expense)}</strong></div>)}</div><div><h3>Despesas por categoria</h3>{Object.entries(reportByCategory).sort((a, b) => b[1] - a[1]).map(([category, total]) => <div className="report-row" key={category}><span>{category}</span><strong className="expense">{formatCurrency(total)}</strong></div>)}</div></div></section>
    </section>{accountForm !== false && <AccountForm account={accountForm} onClose={() => setAccountForm(false)} onSaved={() => { setAccountForm(false); void load() }} />}{transaction && <TransactionForm type={transaction} accounts={accounts} onClose={() => setTransaction(null)} onSaved={() => { setTransaction(null); void load() }} />}{editingTransaction && <TransactionForm type={editingTransaction.type} transaction={editingTransaction.transaction} accounts={accounts} onClose={() => setEditingTransaction(null)} onSaved={() => { setEditingTransaction(null); void load() }} />}
      {profileOpen && <UserProfileForm email={email} onClose={() => setProfileOpen(false)} onSaved={(updatedEmail) => { setProfileOpen(false); window.location.reload(); void updatedEmail }} />}{importOpen && <ImportTransactionsForm onClose={() => setImportOpen(false)} onImported={() => void load()} />}
  </main>
}
