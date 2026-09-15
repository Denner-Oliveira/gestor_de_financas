# Gestor de Finanças

Aplicação full-stack para gestão financeira pessoal e financeira corporativa com autenticação, dashboard financeiro, contas, categorias, importação de transações e controle de autenticação com JWT.

## Visão geral

O projeto possui duas partes principais:

- Backend: FastAPI + SQLAlchemy + SQLite + JWT + Alembic
- Frontend: React + TypeScript + Vite

O backend expõe rotas de autenticação e de movimento financeiro, enquanto o frontend fornece a interface para login, cadastro, dashboard e CRUD de contas/transações.

## Stack tecnológica

### Backend

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic Settings
- JWT com python-jose
- Alembic
- Uvicorn

### Frontend

- React 19
- TypeScript
- Vite
- CSS personalizado

## Estrutura do projeto

```text
backend/
  app/
    core/
    db/
    models/
    routers/
    schemas/
  alembic/
  requirements.txt
  .env
frontend/
  src/
  package.json
```

## Requisitos

Antes de iniciar, instale:

- Python 3.11+ ou 3.13+
- pip
- Node.js 20+
- npm
- Git

## Configuração rápida

### 1) Clonar o repositório

```bash
git clone <url-do-repositorio>
cd gestor_de_financas
```

### 2) Criar ambiente virtual

#### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Instalar dependências do backend

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4) Configurar variáveis de ambiente

O backend utiliza o arquivo `backend/.env` para leitura de configurações, incluindo `JWT_SECRET_KEY`.

Crie o arquivo com o conteúdo mínimo:

```env
JWT_SECRET_KEY="uma_chave_com_mais_de_32_caracteres_gerada_localmente"
```

A aplicação também lê `jwt_algorithm`, `access_token_expire_minutes`, `smtp_*` e `frontend_url`, mas estes possuem valor padrão ou ficam opcionais.

### 5) Rodar as migrações do banco

```bash
cd backend
alembic upgrade head
```

### 6) Iniciar o backend

```bash
cd ..
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### 7) Instalar e iniciar o frontend

```bash
cd frontend
npm install
npm run dev
```

A aplicação frontend deve abrir em:

```text
http://127.0.0.1:5173
```

O backend roda em:

```text
http://127.0.0.1:8000
```

## Endpoints principais

### Autenticação

- `POST /auth/login`
- `POST /auth/registrar`
- `GET /auth/me`
- `PATCH /auth/me`
- `POST /auth/recuperar-senha`

### Financeiro

- CRUD de contas, receitas e despesas
- Dashboard e listagem de transações
- Importação de transações por planilha

## Desenvolvimento

Para rodar o backend em modo desenvolvimento:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Para rodar o frontend em modo desenvolvimento:

```bash
cd frontend
npm run dev
```

## Contribuição

1. Crie uma branch para a funcionalidade.
2. Faça commits com descrições claras.
3. Rode testes e valide a compilação do frontend antes de enviar o pull request.
4. Atualize a documentação quando adicionar ou alterar estrutura, rotas ou configuração.

## Observações

- O backend usa SQLite local no diretório de banco de dados.
- O frontend está configurado para consumir a API em `http://127.0.0.1:8000`.
- Caso queira usar outro host/porta, ajuste o arquivo `frontend/src/services/api.ts`.
