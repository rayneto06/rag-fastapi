# 🧠 RAG FastAPI

Microserviço em **FastAPI** estruturado com **Clean Architecture**, criado para servir como núcleo de um sistema **RAG (Retrieval-Augmented Generation)**.  
Atualmente, o projeto faz o pipeline completo de **ingestão de documentos**, **extração de texto**, **chunking**, e agora **indexação em vector store (in-memory)** — preparando o terreno para integração com **ChromaDB** e LLMs (fase seguinte).

---

## 📂 Estrutura do Projeto

```
rag-fastapi/
│
├─ app/
│  ├─ main.py                     # Cria a aplicação FastAPI e inclui rotas /v1
│  ├─ container.py                # Injeta dependências (domain ⇄ infrastructure)
│  └─ core/
│     ├─ config.py                # Configurações e variáveis de ambiente (.env)
│     └─ logging.py
│
├─ domain/
│  ├─ entities/                   # Entidades de domínio (ex.: Document)
│  ├─ repositories/               # Protocols de persistência de documentos
│  └─ services/                   # Portas (interfaces) para integração
│     ├─ text_extractor.py
│     ├─ chunker.py
│     ├─ chunk_source.py          # Nova interface: fornece chunks de uma origem
│     └─ vector_store.py          # Nova interface: abstrai o repositório vetorial
│
├─ infrastructure/
│  ├─ storage/                    # Implementação local dos repositórios
│  ├─ pdf/                        # Extração de texto de PDFs
│  ├─ chunking/                   # Lógica de divisão em chunks
│  ├─ chunk_sources/
│  │  └─ filesystem_jsonl.py      # Leitor de arquivos .chunks.jsonl
│  └─ vectorstores/
│     └─ in_memory.py             # Vector store simples em memória (para testes)
│
├─ use_cases/
│  ├─ ingest_document.py          # Ingestão completa (upload + parse + chunk)
│  ├─ list_documents.py           # Listagem de documentos
│  ├─ get_document.py             # Detalhes do documento
│  └─ index_document_chunks.py    # NOVO: indexa chunks no vector store
│
├─ interface_adapters/
│  ├─ controllers/
│  │  └─ document_controller.py   # Orquestra os casos de uso
│  ├─ dto/
│  │  └─ document_dto.py          # Schemas de resposta
│  └─ web/api/v1/
│     ├─ documents.py             # Rotas de documentos (POST/GET)
│     └─ health.py                # Healthcheck
│
├─ tests/
│  ├─ test_documents.py           # Testes de upload/listagem de documentos
│  ├─ test_health.py              # Teste básico de /v1/healthz
│  └─ test_index_document_chunks.py  # NOVO: cobre chunk_source + vector_store
│
├─ data/                          # Diretório de dados (criado em runtime)
│
├─ requirements.txt
├─ pytest.ini
├─ .env.example
└─ README.md
```

---

## 🚀 Funcionalidades Atuais

### 🧾 Document Upload
- Endpoint: `POST /v1/documents`
- Faz upload de um PDF, extrai texto, divide em chunks e salva metadados.
- Saída:
  ```json
  {
    "meta": {
      "id": "c19d88e2-499a-4567-8538-bb5a5f82fda4",
      "filename": "c19d88e2-499a-4567-8538-bb5a5f82fda4__ddd.pdf",
      "pages": 12,
      "size_bytes": 571893,
      "created_at": "2025-10-18T14:40:33Z",
      "content_type": "application/pdf"
    },
    "text_path": "data/processed/c19d88e2-499a-4567-8538-bb5a5f82fda4.txt",
    "chunks_path": "data/processed/c19d88e2-499a-4567-8538-bb5a5f82fda4.chunks.jsonl",
    "chunk_count": 2
  }
  ```

### 🧩 Chunk Source (Filesystem)
- Novo adapter `FilesystemJsonlChunkSource` lê os chunks `.jsonl` de `data/processed/`.

### 💾 Vector Store (In-Memory)
- Novo adapter `InMemoryVectorStore` armazena chunks em memória.
- Implementa busca por similaridade textual (Jaccard de tokens).
- Futuramente substituído por **ChromaDB** na camada `infrastructure.vectorstores`.

### ⚙️ Indexação de Chunks
- Caso de uso `IndexDocumentChunks` combina as portas:
  - `ChunkSource` → lê os chunks.
  - `VectorStore` → indexa ou reindexa.
- Pode ser facilmente acionado via Controller ou CLI.

---

## 🧪 Testes

```bash
pytest -q
```

Cobre:
- Ingestão de documentos (pipeline principal).
- Healthcheck.
- Novo fluxo de indexação (`test_index_document_chunks.py`).

Saída esperada:
```
...                                                                   [100%]
3 passed in 1.21s
```

---

## 🧠 Clean Architecture

O projeto mantém o domínio **completamente independente** de frameworks e bibliotecas externas:

```
[ DOMAIN ]  ←  [ USE CASES ]  ←  [ INFRASTRUCTURE / INTERFACE_ADAPTERS ]
(entities,     (business         (FastAPI, Chroma, storage, etc.)
 ports)         logic)
```

Assim, substituições como `InMemoryVectorStore` → `ChromaVectorStore` ocorrem sem alterar o domínio.

---

## 🧭 Próximos Passos

| Etapa | Descrição |
|-------|------------|
| ✅ **1.** | Testes de integração `/v1/documents` finalizados |
| ✅ **2.** | `FilesystemJsonlChunkSource` + `InMemoryVectorStore` criados |
| 🔜 **3.** | Implementar `ChromaVectorStore` (`infrastructure/vectorstores/chroma_store.py`) |
| 🔜 **4.** | Criar endpoint `/v1/rag/index/{document_id}` chamando `IndexDocumentChunks` |
| 🔜 **5.** | Adicionar `QueryRAG` (retrieval + LLM) |
| 🔜 **6.** | Documentar exemplos de queries RAG e integração com LLM Provider |

---

## 🧰 Execução Local

### Ambiente
```bash
cp .env.example .env
```
Configure os diretórios de dados (padrão):
```
DATA_DIR=./data
RAW_DIR=./data/raw
PROCESSED_DIR=./data/processed
INDEX_DIR=./data/index
```

### Rodar servidor
```bash
uvicorn app.main:app --reload --port 8000
```

### Testar API
- `POST /v1/documents` — upload PDF  
- `GET /v1/documents` — lista  
- `GET /v1/documents/{id}` — detalhes  
- `GET /v1/healthz` — status

---

## 🧩 Tecnologias

| Categoria | Stack |
|------------|-------|
| Framework | FastAPI |
| Testes | pytest + httpx |
| Arquitetura | Clean Architecture (Domain-Driven Design simplificado) |
| Extração de texto | PyPDF |
| Armazenamento local | FileSystem |
| Vector Store (fase 1) | InMemory |
| Próxima Etapa | ChromaDB + QueryRAG |

---

## 📜 Licença

MIT © 2025  
Projeto acadêmico com fins de estudo.
