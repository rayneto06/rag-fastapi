# RAG FastAPI

RAG FastAPI é um projeto de referência em **Clean Architecture** para experimentos de
**Retrieval-Augmented Generation (RAG)** com **FastAPI**. O objetivo é oferecer uma base
sólida, testável e bem documentada para **upload**, **ingestão** e **consulta** (query) de
documentos, com **vector store local (Chroma)** e endpoints REST claros.

> Status atual: projeto estável, testado e sanitizado (mypy, ruff, black 100% verdes).

---

## 🚀 Visão geral

- **Upload** de PDFs via API.
- **Ingestão**: particionamento/normalização e indexação no **Chroma**.
- **Consulta (Query)**: recuperação (retrieval-first) a partir do índice vetorial.
- **Clean Architecture**: domínio e casos de uso desacoplados de frameworks e de infraestrutura.
- **Testes**: unitários e E2E cobrindo o fluxo principal.

---

## 🧱 Arquitetura (camadas)

```
app/
├─ domain/                # Entidades e contratos puros (sem dependências externas)
├─ use_cases/             # Orquestra lógica de negócio; usa apenas interfaces do domínio
├─ infrastructure/        # Implementações (ex.: Chroma, FS local, parsers)
└─ interface_adapters/    # Web/API (FastAPI), DTOs, mapeamentos de entrada/saída
tests/                    # Unit e E2E
```

**Princípios-chave**
- Domínio independente de frameworks.
- Use cases finos, orquestrando repositórios/serviços via interfaces.
- Adaptadores plugáveis na infraestrutura (ex.: trocar Chroma por pgvector futuramente).
- Interface (FastAPI) apenas expõe/recebe dados (DTOs), sem lógica de negócio.

---

## 🗺️ Diagrama de fluxo

<img width="2232" height="396" alt="fluxo mermaid" src="https://github.com/user-attachments/assets/7926a506-7201-494b-b5db-6485c3b61f71" />

---

## 📦 Requisitos

- Python 3.11+
- pip / venv (ou uv / poetry, se preferir)
- (Opcional) `uvicorn` para execução local
- (Opcional) `pre-commit` para ganchos (ruff, black, trailing-whitespace, mypy)

---

## ⚙️ Configuração

1) **Clonar o repositório**

```bash
git clone https://github.com/rayneto06/rag-fastapi.git
cd rag-fastapi
```

2) **Criar e ativar o virtualenv**

```bash
python -m venv .venv
source .venv/bin/activate            # Linux/Mac
# ou
.\.venv\Scriptsctivate             # Windows
```

3) **Instalar dependências**

```bash
pip install -U pip
pip install -r requirements.txt
```

4) **Arquivo `.env`**

Copie o `.env.example` para `.env` e ajuste os valores conforme seu ambiente:

```bash
cp .env.example .env
```

**Variáveis importantes**
- `APP_PORT`: porta do servidor (ex.: 8000)
- `APP_ENV`: ambiente (ex.: local)
- `CORS_ORIGINS`: JSON com origens permitidas
- `DATA_DIR`, `RAW_DIR`, `PROCESSED_DIR`, `INDEX_DIR`: diretórios de dados
- `VECTOR_STORE_PROVIDER`: `chroma`
- `CHROMA_DIR`, `CHROMA_COLLECTION`: diretório e coleção do Chroma
- `KEEP_TEST_DATA`: se `1`, mantém arquivos gerados pelos testes E2E
- `ANONYMIZED_TELEMETRY`: desligar/ligar telemetria de libs (quando aplicável)

> Observação: caminhos relativos são resolvidos a partir da raiz do projeto.

---

## ▶️ Execução local

```bash
uvicorn app.main:app --reload --port ${APP_PORT:-8000}
# API em: http://127.0.0.1:${APP_PORT:-8000}
```

### Rotas principais (v1)

- `POST /v1/documents` – upload de PDF (gera entrada em RAW, processa e indexa)
- `GET  /v1/documents` – lista documentos
- `GET  /v1/documents/{document_id}` – detalhes de um documento
- `POST /v1/rag/query` – consulta (retrieval-first) no índice vetorial

---

## 🧪 Testes

### Rodar a suíte completa

```bash
pytest -q
```

### Linters e type checking

```bash
ruff .
black --check .
mypy .
```

### Pre-commit (opcional, mas recomendado)

```bash
pre-commit install
pre-commit run -a
```

---

## 🔍 Testes E2E (resumo do que validam)

Os E2E cobrem o **fluxo real de uso via API**, garantindo que:

1. `POST /v1/documents` aceita um PDF de teste, armazena em **RAW**, processa e
   executa a **ingestão** (particionamento/normalização) para **PROCESSED**.
2. A **indexação** no **Chroma** é invocada e não gera exceções de integração.
3. `GET /v1/documents` retorna o documento recém-enviado com metadados esperados.
4. `POST /v1/rag/query` acessa o índice e retorna uma estrutura de **hits** (retrieval-first).
   - Dependendo do conteúdo do PDF de teste e da parametrização, a lista pode vir vazia,
     porém a **integração** (request/response, pipeline de retrieval) é verificada.
5. `KEEP_TEST_DATA=0` limpa artefatos ao final; com `KEEP_TEST_DATA=1`, mantém para inspeção.

Esses testes conferem **contratos de API**, **caminhos de dados** e a **orquestração** entre camadas,
sem quebrar a independência do domínio/casos de uso.

---

## 🧩 Decisões de arquitetura (resumo)

- **Vector Store:** **Chroma** local para simplicidade e velocidade em desenvolvimento.
  A interface de repositório no domínio permite **substituição futura** (ex.: pgvector)
  sem impacto no **use case** ou na camada web.
- **Clean Architecture:** domínio e casos de uso **imutáveis** nesta fase; toda evolução é feita
  via infraestrutura/adapters, preservando testabilidade e clareza.
- **DTOs e validações:** definidos nos adapters para manter o domínio livre de detalhes HTTP.

---

## 🔜 Próximos passos

- Implementar **geração** (o “G” do RAG) por trás do endpoint de query (mantendo a mesma
  interface de retrieval).
- Adicionar **observabilidade** (logs, métricas) por caso de uso.
- Suporte a **outros provedores** de vector store via o mesmo contrato do domínio.

---

## 📄 Licença

MIT.

---
