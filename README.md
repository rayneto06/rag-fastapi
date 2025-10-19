# RAG FastAPI

Projeto de **Retrieval-Augmented Generation (RAG)** com arquitetura limpa e modular, desenvolvido em **FastAPI**.

---

## 🧱 Estrutura e objetivos

Este serviço fornece a base de um microserviço de RAG voltado à ingestão de documentos, armazenamento de embeddings e consultas semânticas.

A arquitetura segue **Clean Architecture** e isola completamente as dependências de infraestrutura — permitindo alternar entre diferentes repositórios ou provedores de embeddings sem impactar o domínio.

```
rag-fastapi/
├── app/                     # Inicialização, container e configuração
├── domain/                  # Entidades e interfaces puras
├── use_cases/               # Casos de uso independentes
├── infrastructure/           # Implementações concretas (PDF, Chroma, storage, etc.)
├── interface_adapters/      # Controllers e rotas FastAPI
└── tests/                   # Testes unitários e de integração
```

---

## ⚙️ Funcionalidades atuais

### ✅ Documentos
- Upload de PDFs com extração de texto e chunking automático.
- Salvamento de artefatos (texto e chunks) em disco.
- Indexação automática dos chunks no **Vector Store** configurado (`InMemory` ou **Chroma**).
- Listagem e obtenção de metadados de documentos.

### ✅ Vector Store
- Implementações:
  - `InMemoryVectorStore`: volátil, ideal para testes e CI.
  - `ChromaVectorStore`: persistente e local, usando `chromadb`.
- Indexação e busca por similaridade (L2 → escore invertido em 1/(1+d)).

### ✅ RAG (Retrieval-Only por enquanto)
- Endpoint `/v1/rag/query` para consulta de relevância textual com `top_k` ajustável.
- Suporte a diferentes provedores de embeddings via contrato `VectorStore`.

### ✅ Healthcheck
- `/v1/health` para verificação de status e versão.

### ✅ Testes
- Suíte `pytest` completa e passando: ingestão, listagem, query e integração com Chroma.

### ✅ Postman
- Coleção e ambiente prontos (`RAG_FastAPI.postman_collection.json` e `RAG_FastAPI.postman_environment.json`)
  - Upload → List → Get → Query já configurados.

---

## 🧩 Configuração via `.env`

```bash
APP_PORT=8000
APP_ENV=local

CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
VECTOR_STORE_PROVIDER=chroma      # ou inmemory
CHROMA_DIR=.chroma
CHROMA_COLLECTION=rag_chunks
DATA_DIR=./data
RAW_DIR=./data/raw
PROCESSED_DIR=./data/processed
INDEX_DIR=./data/index
KEEP_TEST_DATA=0
ANONYMIZED_TELEMETRY=FALSE
```

---

## 🚀 Executar localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar API
uvicorn app.main:app --reload

# Rodar testes
pytest -q
```

A API ficará disponível em `http://127.0.0.1:8000`  
A documentação interativa (Swagger) está em `http://127.0.0.1:8000/docs`

---

## 🔮 Próximo passo

### 🧠 Fase seguinte: **LLMProvider e geração de respostas**
Implementar o caso de uso `QueryRAG` completo, com:
1. **Interface `LLMProvider` no domínio** para abstrair qualquer modelo de linguagem.
2. **Implementação local (ex: OllamaProvider)** para geração baseada no contexto recuperado.
3. **Integração no endpoint `/v1/rag/query`**: combinar *retrieval + geração*.
4. **Testes de integração** com mocks determinísticos para o LLM.
