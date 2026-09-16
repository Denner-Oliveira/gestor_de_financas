# Guia de instalação no Windows

Este guia mostra como instalar o projeto Gestor de Finanças do zero no Windows.

## Requisitos

- Python 3.11+ ou 3.13+
- Git
- Node.js 20+
- npm

## 1) Clonar o projeto

```powershell
git clone <url-do-repositorio>
cd gestor_de_financas
```

## 2) Criar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a execução de scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3) Instalar dependências do backend

```powershell
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

## 4) Configurar o arquivo de ambiente

Crie o arquivo `backend/.env` com a chave JWT:

```env
JWT_SECRET_KEY="uma_chave_com_mais_de_32_caracteres_gerada_localmente"
```

Você pode usar uma chave simples, desde que tenha pelo menos 32 caracteres.

## 5) Inicializar o banco de dados

```powershell
cd backend
alembic upgrade head
```

## 6) Rodar o backend

```powershell
cd ..
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## 7) Instalar dependências do frontend

```powershell
cd frontend
npm install
```

## 8) Rodar o frontend

```powershell
npm run dev
```

No computador, acesse:

```text
http://127.0.0.1:5173
```

Para acessar por outro dispositivo conectado à mesma rede Wi-Fi, descubra o IPv4
do computador com `ipconfig` e abra `http://SEU_IPV4:5173` no dispositivo.
Use o mesmo IPv4 para a API, na porta `8000`.

## 9) Problemas comuns

### `npm` bloqueado no PowerShell

Use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### `vite` não reconhecido

Quando a instalação do frontend ainda não terminou, execute:

```powershell
npm install
npm run dev
```

### JWT_SECRET_KEY faltando

Crie o arquivo `backend/.env` com a variável `JWT_SECRET_KEY`.
