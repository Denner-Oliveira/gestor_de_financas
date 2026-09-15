# Guia de instalação no Linux

Este guia mostra como instalar o projeto Gestor de Finanças do zero no Linux.

## Requisitos

- Python 3.11+ ou 3.13+
- Git
- Node.js 20+
- npm

## 1) Clonar o projeto

```bash
git clone <url-do-repositorio>
cd gestor_de_financas
```

## 2) Criar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Instalar dependências do backend

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

## 4) Configurar o arquivo de ambiente

Crie o arquivo `backend/.env` com a chave JWT:

```env
JWT_SECRET_KEY="uma_chave_com_mais_de_32_caracteres_gerada_localmente"
```

## 5) Inicializar o banco de dados

```bash
cd backend
alembic upgrade head
```

## 6) Rodar o backend

```bash
cd ..
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

## 7) Instalar dependências do frontend

```bash
cd frontend
npm install
```

## 8) Rodar o frontend

```bash
npm run dev
```

Acesse:

```text
http://127.0.0.1:5173
```

## 9) Problemas comuns

### `vite` não reconhecido

Se o npm não encontrar o binário local do Vite, rode:

```bash
npm install
npm run dev
```

### `JWT_SECRET_KEY` faltando

Crie o arquivo `backend/.env` com `JWT_SECRET_KEY`.
