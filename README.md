# Gestor de Finanças

Aplicação full-stack para controle financeiro pessoal. O sistema permite cadastrar
usuários, contas financeiras, receitas e compras, acompanhar parcelas, consultar
um dashboard mensal, gerar relatórios por período e importar lançamentos por
planilha XLSX.

## Funcionalidades

- Cadastro e login de usuários com JWT.
- Access token e refresh token com rotação automática.
- Logout com revogação do refresh token.
- Alteração de e-mail e senha.
- Recuperação de senha por token de uso único e expiração limitada.
- Isolamento dos dados por usuário.
- Criação automática da conta padrão "Dinheiro em espécie".
- CRUD de contas financeiras.
- CRUD de receitas.
- CRUD de compras à vista ou parceladas.
- Bloqueio de alterações estruturais em compras com parcelas já pagas.
- Dashboard mensal com:
  - saldo;
  - receitas;
  - despesas;
  - contas;
  - movimentações;
  - resumo rápido do mês.
- Relatório geral com período configurável.
- Gráficos agrupados por mês, categoria ou conta:
  - pizza como padrão;
  - barras horizontais;
  - colunas;
  - linha.
- Agrupamento visual de fatias pequenas em "Outros".
- Download de modelo XLSX e importação transacional de lançamentos.
- Logs de acesso no console e logs de warnings/errors/critical em arquivo.

## Arquitetura

O projeto é um monorepo com dois componentes independentes:

```text
backend/
  app/
    core/          # configurações, segurança, e-mail e logging
    db/            # engine e dependências de sessão
    models/        # modelos SQLAlchemy
    routers/       # autenticação, contas, lançamentos, relatórios e importações
    schemas/       # schemas Pydantic
  alembic/         # migrations do banco
  requirements.txt

frontend/
  src/
    components/
    pages/
    services/
    types/
    utils/
  package.json
```

## Stack

### Backend

- Python 3.11+
- FastAPI
- SQLAlchemy 2
- SQLite
- Alembic
- Pydantic Settings
- JWT com `python-jose`
- Uvicorn
- `openpyxl` para importação e exportação XLSX

### Frontend

- React 19
- TypeScript
- Vite
- CSS personalizado

## Requisitos

- Python 3.11 ou superior
- pip
- Node.js 20 ou superior
- npm
- Git

## Configuração local

### 1. Clonar o projeto

```bash
git clone <url-do-repositorio>
cd gestor_de_financas
```

### 2. Criar e ativar o ambiente virtual

#### Windows PowerShell

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências do backend

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4. Configurar o backend

Crie `backend/.env`. O campo obrigatório é uma chave JWT com pelo menos
32 caracteres:

```env
JWT_SECRET_KEY="gere-uma-chave-secreta-com-pelo-menos-32-caracteres"
```

Configurações disponíveis:

```env
JWT_SECRET_KEY="chave-obrigatoria"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL="http://127.0.0.1:5173"

# Opcionais, usados para recuperação de senha por e-mail
SMTP_HOST=""
SMTP_PORT=587
SMTP_USERNAME=""
SMTP_PASSWORD=""
SMTP_FROM=""
```

Não versione `backend/.env`, senhas SMTP, chaves JWT ou tokens.

### 5. Executar as migrations

As tabelas devem ser criadas e alteradas por migrations do Alembic:

```bash
cd backend
alembic upgrade head
cd ..
```

O banco SQLite é criado em:

```text
backend/app/db/financas.db
```

Para criar uma nova migration após alterar os modelos:

```bash
cd backend
alembic revision -m "descricao_da_alteracao"
```

Revise a migration gerada antes de executar `alembic upgrade head`.

### 6. Iniciar o backend

Na raiz do projeto:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Para acessar pela rede local, use o IPv4 do computador (obtido com `ipconfig` no
Windows ou `ip addr` no Linux) no navegador do outro dispositivo:

```text
http://SEU_IPV4:5173
```

O frontend usa automaticamente esse mesmo endereço para chamar a API na porta
`8000`. Computador e celular precisam estar na mesma rede Wi-Fi, e o Firewall
do sistema deve permitir as portas `5173` e `8000`.

Documentação interativa da API:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

### 7. Configurar e iniciar o frontend

Opcionalmente, crie `frontend/.env.local` para apontar para outra API:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Depois instale as dependências e inicie o Vite:

```bash
cd frontend
npm install
npm run dev
```

A interface estará disponível normalmente em
`http://127.0.0.1:5173`.

## API

Todas as rotas financeiras exigem o header:

```text
Authorization: Bearer <access_token>
```

### Autenticação

| Método | Rota | Descrição |
| --- | --- | --- |
| POST | `/auth/registrar` | Cria um usuário |
| POST | `/auth/login` | Realiza login e retorna tokens |
| PATCH | `/auth/me` | Atualiza os dados do usuário autenticado |
| POST | `/auth/refresh` | Rotaciona o refresh token |
| POST | `/auth/logout` | Revoga o refresh token |
| POST | `/auth/recuperar-senha` | Solicita recuperação de senha |
| POST | `/auth/redefinir-senha` | Define uma nova senha |

### Contas e lançamentos

| Método | Rota | Descrição |
| --- | --- | --- |
| POST/GET | `/contas` | Cria ou lista contas |
| PATCH/DELETE | `/contas/{conta_id}` | Atualiza ou exclui uma conta |
| POST/GET | `/receitas` | Cria ou lista receitas |
| PATCH/DELETE | `/receitas/{receita_id}` | Atualiza ou exclui uma receita |
| POST/GET | `/compras` | Cria ou lista compras |
| PATCH/DELETE | `/compras/{compra_id}` | Atualiza ou exclui uma compra |

### Relatórios e importação

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/relatorios/geral` | Gera relatório entre `inicio` e `fim` |
| GET | `/importacoes/modelo` | Baixa o modelo XLSX |
| POST | `/importacoes/lancamentos` | Importa lançamentos de uma planilha |

O modelo de importação possui as colunas:

```text
tipo, descricao, categoria, valor, data, conta,
quantidade_parcelas, observacoes
```

O arquivo inteiro é validado antes das inserções. O limite de upload é 10 MB.

## Logs

Os acessos HTTP são exibidos somente no console, sem payloads, tokens ou
credenciais:

```text
SUCESSO | GET /health | status=200 | duracao_ms=...
FALHA | GET /rota-inexistente | status=404 | duracao_ms=...
```

Mensagens `WARNING`, `ERROR` e `CRITICAL`, incluindo warnings capturados do
Python, são gravadas em:

```text
backend/logs/app.log
```

O arquivo possui rotação automática de 5 MB e mantém até 5 backups. O diretório
de logs é ignorado pelo Git.

## Desenvolvimento e validação

Backend:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm run dev
npm run build
npm run lint
```

Antes de abrir um pull request:

1. Execute as migrations em um banco local.
2. Confirme o login, refresh e logout.
3. Teste contas, receitas, compras e parcelas.
4. Teste o relatório e a importação XLSX.
5. Execute o build do frontend.
6. Verifique `git diff --check`.

## Deploy

O repositório deve ser configurado como dois componentes em plataformas que
exigem detecção individual:

- Backend: diretório `backend`, iniciado com Uvicorn.
- Frontend: diretório `frontend`, publicado como aplicação estática.

No frontend, configure `VITE_API_URL` com a URL pública do backend. No backend,
configure `FRONTEND_URL` com a URL pública do frontend.

SQLite é adequado para desenvolvimento local, mas pode perder dados quando o
serviço é recriado ou o disco não é persistente. Para produção, recomenda-se
migrar para PostgreSQL antes do deploy definitivo.
