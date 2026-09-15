import { useState, type ChangeEvent } from 'react'
import { downloadImportTemplate, importTransactions } from '../services/api'

type Props = { onClose: () => void; onImported: () => void }

export function ImportTransactionsForm({ onClose, onImported }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null
    setFile(selected)
    setError('')
    setMessage('')
  }

  async function importFile() {
    if (!file) {
      setError('Selecione um arquivo XLSX.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const response = await importTransactions(file)
      if (!response.ok) {
        const data = await response.json().catch(() => null) as { detail?: string } | null
        throw new Error(data?.detail ?? 'Não foi possível importar o arquivo.')
      }
      const data = await response.json() as { importados: number }
      setMessage(`${data.importados} lançamento(s) importado(s) com sucesso.`)
      onImported()
    } catch (importError) {
      setError(
        importError instanceof TypeError
          ? 'Não foi possível conectar à API. Confirme se o backend está ativo e se o frontend está usando a porta autorizada.'
          : importError instanceof Error
            ? importError.message
            : 'Não foi possível importar o arquivo.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="login-card account-form import-form">
        <div className="section-heading">
          <h2>Importar lançamentos</h2>
          <button type="button" className="link-button" onClick={onClose}>Fechar</button>
        </div>
        <p className="import-help">
          Preencha o modelo com uma linha por receita ou compra. O nome da conta deve ser igual ao cadastrado.
        </p>
        <button type="button" className="secondary" onClick={() => void downloadImportTemplate()}>
          Baixar modelo XLSX
        </button>
        <label>
          Arquivo XLSX
          <input type="file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" onChange={selectFile} />
        </label>
        {file && <p className="import-file">{file.name}</p>}
        {error && <p className="form-error">{error}</p>}
        {message && <p className="form-success">{message}</p>}
        <button type="button" onClick={() => void importFile()} disabled={loading}>
          {loading ? 'Importando...' : 'Importar arquivo'}
        </button>
      </div>
    </div>
  )
}
