# 🔗 How everything connects

Nothing here is a separate tutorial. Each idea exists because the previous one wasn't enough.

```text
PostgreSQL ──────→ SQL
     ↓
Database Design
     ↓
Transactions
     ↓
Indexes
     ↓
Performance
     ↓
NoSQL ───────────→ MongoDB / Redis
     ↓
Vector Search
     ↓
FAISS ────────────→ Similarity Search
     ↓
Chroma ───────────→ RAG
     ↓
Embeddings
     ↓
LLMs
     ↓
AI Agents
```

## The "because" chain

| Step | Because... |
|---|---|
| PostgreSQL → SQL | a database is useless until I can ask it questions |
| SQL → Design | queries get painful when tables are badly shaped |
| Design → Transactions | well-shaped tables still break if two users write at once |
| Transactions → Indexes | safe is good; *fast* is also needed |
| Indexes → Performance | a read of a million rows needs a plan, not luck |
| Performance → NoSQL | some data (documents, caches) fits a different shape better |
| NoSQL → Vector search | none of them can ask "what *means* the same?" |
| Vector search → FAISS | the raw maths of nearest neighbours, made fast |
| FAISS → Chroma | I also need to store text + metadata and filter |
| Chroma → RAG | retrieved chunks make an LLM answer from *my* data |
| RAG → Agents | combine SQL facts + vector memory + tools |

## Which database for which problem?

```text
Need exact answers, rules, money, joins?        → PostgreSQL
Need flexible nested documents?                 → MongoDB
Need microsecond reads / expiring data?         → Redis
Need "find similar" / semantic search / RAG?    → FAISS / Chroma / pgvector
Need all of it?                                 → Project 8
```

## Connection strings (one place)

Used by the projects. Put real values in a `.env` file (git-ignored) — never commit them. See [`10-database-security/.env.example`](10-database-security/.env.example).

| Service | Start it | Connection string |
|---|---|---|
| PostgreSQL | `docker run -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres:16` | `postgresql://postgres:secret@localhost:5432/shop` |
| MongoDB | `docker run -p 27017:27017 -d mongo:7` | `mongodb://localhost:27017` |
| Redis | `docker run -p 6379:6379 -d redis:7` | `redis://localhost:6379` |
| Chroma | nothing to start — `chromadb.PersistentClient(path="./chroma_store")` | local folder |
| FAISS | nothing to start — it's a library | local `*.index` file |

> The Python scripts use `host=localhost user=postgres` with no password for convenience on a local test machine. For anything real, set a password and use environment variables.

## Concepts that appear in several places

| Concept | Where it shows up |
|---|---|
| **Index** | B-tree (06) · MongoDB index (07) · FAISS index (09) — all trade space for speed |
| **Transaction / atomicity** | SQL (03) · concurrency (05) · distributed 2PC / saga (08) |
| **CAP / consistency** | fundamentals (01) · replicas (08) · cache staleness (Redis, 07) |
| **Metadata filter** | `WHERE` in SQL · `where=` in Chroma · security boundary in agent memory (12) |
| **Least privilege** | roles (10) · read-only role for Text-to-SQL (12) |
| **Cache invalidation** | Redis TTL (07) · Project 5 · Project 8 |
