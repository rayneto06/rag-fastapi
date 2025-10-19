# 🧠 RAG FastAPI

API modular para experimentos com **Retrieval-Augmented Generation (RAG)** usando **FastAPI** e **Clean Architecture**.

Este projeto faz parte de um estudo de arquitetura de software e IA generativa, com foco em separação clara de camadas e testabilidade.

---

## 🚀 Estrutura do projeto

```
rag-fastapi/
├── app/
│   ├── main.py                    # Inicialização da API FastAPI
│   ├── container.py               # Injeção de dependências (Clean Architecture)
│   └── core/                      # Configurações globais
├── domain/
│   ├── services/                  # Portas (interfaces) como VectorStore, Chunker, etc.
│   └── use_cases/                 # Casos de uso independentes de infraestrutura
├── infrastructure/
│   ├── vectorstores/in_memory.py  # Vector Store inicial (in-memory)
│   ├── pdf/                       # Extração de texto
│   ├── chunking/                  # Divisão em chunks
│   └── storage/                   # Repositório local de documentos
├── interface_adapters/
│   ├── web/api/v1/                # Rotas HTTP organizadas por módulo
│   └── controllers/               # Controladores (camada intermediária)
├── tests/
│   └── test_rag_query.py          # Teste de integração do endpoint /v1/rag/query
```

---

## 🧬 Funcionalidades atuais

| Funcionalidade                   | Descrição                                       | Status         |
| -------------------------------- | ----------------------------------------------- | -------------- |
| Upload de documentos PDF         | Faz upload e armazena metadados                 | ✅              |
| Listagem e detalhe de documentos | `/v1/documents`, `/v1/documents/{id}`           | ✅              |
| Healthcheck                      | `/v1/health`                                    | ✅              |
| **Consulta RAG (retrieval)**     | `/v1/rag/query` — retorna chunks mais similares | ✅              |
| Vector Store In-Memory           | Implementação inicial (sem persistência)        | ✅              |
| Indexação automática             | Ainda não implementada                          | ⏳ Próxima fase |

---

## ⚙️ Como rodar localmente

### 1️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 2️⃣ Rodar testes

```bash
pytest -q
```

### 3️⃣ Rodar servidor local

```bash
uvicorn app.main:app --reload
```

### 4️⃣ Endpoints principais

| Método | Endpoint             | Descrição                   |
| ------ | -------------------- | --------------------------- |
| GET    | `/v1/health`         | Healthcheck                 |
| POST   | `/v1/documents`      | Upload de documento PDF     |
| GET    | `/v1/documents`      | Listar documentos           |
| GET    | `/v1/documents/{id}` | Obter detalhes do documento |
| POST   | `/v1/rag/query`      | Consulta RAG (retrieval)    |

---

## 🥪 Testes

Os testes usam `pytest` com `pytest-asyncio` e `httpx.AsyncClient` via `ASGITransport`.

```bash
pytest -q
```

Saída esperada:

```
10 passed in X.XXs
```

---

## 🤀 Próximos passos planejados

1. **Implementar Vector Store persistente (Chroma)**

   * Substituir o InMemoryVectorStore por uma versão local persistente.
2. **Adicionar caso de uso e endpoint de indexação de chunks**

   * Populando o Vector Store a partir dos `.jsonl` gerados.
3. **Integração com LLMProvider (Ollama ou local)**

   * Completar o “G” do RAG.
4. **Documentação e scripts de inicialização automatizados.**

---

## 🗞️ Licença

MIT License
