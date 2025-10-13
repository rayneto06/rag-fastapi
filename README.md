# 📘 README.md — RAG FastAPI (Local | Clean Architecture | Portfólio FIAP)

## 🧠 Visão Geral

Este projeto implementa uma **API de RAG (Retrieval-Augmented Generation)** construída em **FastAPI**, organizada segundo os princípios de **Clean Architecture**, preparado para integrações futuras com LLMs.

A aplicação está sendo desenvolvida em camadas bem definidas:
- **Domain** → Entidades, Repositórios e Interfaces (sem dependências externas)
- **Use Cases** → Regras de negócio puras e independentes de infraestrutura
- **Interface Adapters** → Controllers, DTOs e APIs (FastAPI)
- **Infrastructure** → Implementações concretas (armazenamento local, extração de texto via `pypdf`, chunking, etc.)
- **App/Core** → Configurações, logging e injeção de dependências (Container)

---

## ⚙️ Estrutura de Pastas

```
rag-fastapi/
├─ app/
│  ├─ core/                 # Configurações e logging
│  ├─ container.py          # Injeção de dependências
│  ├─ main.py               # Criação da aplicação FastAPI
│  └─ version.py
│
├─ domain/
│  ├─ entities/             # Entidades de negócio (Document)
│  ├─ repositories/         # Interfaces de repositórios
│  └─ services/             # Interfaces de serviços (extrator, chunker)
│
├─ use_cases/
│  ├─ ingest_document.py    # Upload e processamento de PDFs
│  ├─ list_documents.py     # Listagem de documentos
│  └─ get_document.py       # Detalhamento de documento
│
├─ interface_adapters/
│  ├─ controllers/          # Controladores (camada intermediária)
│  ├─ dto/                  # Schemas Pydantic para API
│  └─ web/api/v1/           # Rotas FastAPI (v1)
│
├─ infrastructure/
│  ├─ storage/              # Repositório local (filesystem)
│  ├─ pdf/                  # Extração de texto com pypdf
│  └─ chunking/             # Chunker simples
│
├─ data/                    # Dados locais
│  ├─ raw/
│  ├─ processed/
│  └─ index/
│
├─ tests/                   # Testes automatizados (pytest)
│  ├─ conftest.py           # Limpeza automática dos diretórios
│  ├─ test_health.py
│  └─ test_documents.py
│
├─ .env.example             # Exemplo de configuração
├─ requirements.txt
├─ pytest.ini
├─ .pre-commit-config.yaml
└─ README.md
```

---

## 🚀 Funcionalidades Atuais

| Endpoint | Método | Descrição |
|-----------|---------|------------|
| `/v1/healthz` | GET | Verifica o status da API |
| `/v1/documents` | POST | Faz upload de um arquivo PDF e processa (texto + chunks) |
| `/v1/documents` | GET | Lista os documentos processados |
| `/v1/documents/{doc_id}` | GET | Retorna metadados e caminhos do documento processado |

---

## 🧩 Tecnologias e Bibliotecas

- **FastAPI** — framework web
- **pypdf** — leitura e extração de texto de PDFs
- **httpx** — cliente HTTP assíncrono (testes)
- **pytest** — testes automatizados
- **ruff / black / mypy** — qualidade e estilo de código
- **Clean Architecture** — separação clara de camadas
- **Pre-commit hooks** — lint, type-check e format automáticos

---

## 💻 Como Executar Localmente

### 1️⃣ Clonar o repositório
```bash
git clone <seu-repo-url> rag-fastapi
cd rag-fastapi
```

### 2️⃣ Criar ambiente virtual
```bash
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
```

### 3️⃣ Instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente
```bash
cp .env.example .env
```

Você pode ajustar:
```ini
APP_PORT=8000
KEEP_TEST_DATA=0  # Se =1, mantém arquivos criados nos testes
```

### 5️⃣ Rodar servidor local
```bash
uvicorn app.main:app --reload --port 8000
```

### 6️⃣ Acessar a API
- Swagger UI → http://127.0.0.1:8000/docs  
- Healthcheck → http://127.0.0.1:8000/v1/healthz

---

## 🧠 Exemplos de Uso

### Upload de PDF
```bash
curl -X POST http://127.0.0.1:8000/v1/documents \
  -F "file=@/caminho/para/arquivo.pdf"
```

### Listar documentos
```bash
curl http://127.0.0.1:8000/v1/documents
```

### Consultar documento específico
```bash
curl http://127.0.0.1:8000/v1/documents/<id>
```

---

## 🧪 Testes

### Rodar todos os testes
```bash
pytest -q
```

### Com saída detalhada
```bash
pytest -v
```

Os testes incluem:
- Healthcheck funcional
- Upload, listagem e detalhe de documentos
- Fixture automática (`conftest.py`) que limpa `data/raw` e `data/processed` antes e depois da execução,  
  **a menos que `KEEP_TEST_DATA=1` no `.env`**

---

## 🧰 Qualidade de Código

Formatar e verificar tudo:
```bash
black .
ruff check . --fix
mypy app
```

Instalar pre-commit (opcional, mas recomendado):
```bash
pre-commit install
```

---

## 🧭 Próximos Passos

1. ✅ **Testes de integração** — `/v1/documents` (upload/list/get) usando `ASGITransport` (já implementado).  
2. ⚙️ **Implementar vector store local (Chroma)** como repositório na camada de infraestrutura, com interface no domínio.  
3. 💬 **Criar use case `QueryRAG`** e endpoint `/v1/rag/query` (retrieval primeiro, depois geração).  
4. 🤖 **Definir interface `LLMProvider`** no domínio e implementação local (ex.: Ollama) para completar o “G” do RAG.  
5. 🧱 **Manter Clean Architecture estrita**, documentação atualizada e README refinado como portfólio FIAP.

---

## 🏗️ Arquitetura (Clean Architecture)

```
[FastAPI Routers] ─► [Controllers / DTOs] ─► [Use Cases] ─► [Domain Entities & Interfaces] ◄── [Infrastructure Impl]
```

- Fluxo de dependência **sempre para dentro**
- Camadas externas podem mudar sem afetar as internas
- Ideal para trocar componentes (LLM, vetor store, storage) com mínimo impacto

---

## 🪪 Autor

**Raymundo Neto**    
📧 Contato profissional: *raymundocneto@gmail.com*  
💼 Portfólio: *[LinkedIn](https://www.linkedin.com/in/raymundo-neto-61933427/)*  
