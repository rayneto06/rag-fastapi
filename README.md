# RAG FastAPI (Local, Portfólio FIAP)

API organizada com FastAPI para servir um pipeline de RAG local, começando por:
- estrutura limpa (camadas, configs via .env, testes e linters)
- endpoint de healthcheck
- diretórios preparados para ingestão de PDFs e índice local

## Requisitos
- Python 3.12
- Git

## Setup
```bash
# clonar e entrar
git clone <seu-repo-url> rag-fastapi
cd rag-fastapi

# ambiente virtual
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# instalar deps
pip install --upgrade pip
pip install -r requirements.txt

# configurar env
cp .env.example .env

# (opcional) pre-commit
pre-commit install
