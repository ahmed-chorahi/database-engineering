# 12 · AI + Database Integration

> Where everything I learned finally meets LLMs. The databases don't change — they become the **memory and the facts** the model is missing.

Files: [`text_to_sql.py`](text_to_sql.py) · [`agent_memory.py`](agent_memory.py) · [`embed.py`](embed.py)

## The big picture

```text
                User
                  ↓
              AI Agent
             /        \
            ↓          ↓
     PostgreSQL      Chroma
     Structured      Vectors
        Data          Data
            \          /
             ↓        ↓
              Retrieval
                  ↓
               LLM
                  ↓
               Answer
```

**The core idea:** an LLM is a brilliant reader with a bad memory and no access to *your* data. Databases give it:

| Gap | Fixed by |
|---|---|
| doesn't know my private/current data | retrieval (SQL or vector) |
| makes up facts | ground the answer in retrieved rows/chunks |
| forgets between chats | persistent memory |
| can't do exact math/counts | let SQL do it |

## 1. Structured + unstructured data

| | Structured | Unstructured |
|---|---|---|
| Example | orders, users, prices | manuals, emails, PDFs, tickets |
| Store | PostgreSQL | text → embeddings → Chroma/FAISS/pgvector |
| Ask with | SQL (exact) | similarity search (meaning) |
| Wrong tool = | vector search for "total sales" ❌ | SQL `LIKE` for "documents about refunds" ❌ |

> **Rule of thumb:** *counts, sums, filters, joins → SQL. Meaning, fuzzy matching, "find something like this" → vectors.*

## 2. LLM + PostgreSQL: Text-to-SQL

```text
Question ─► LLM (given the SCHEMA) ─► SQL ─► VALIDATE ─► run as READ-ONLY role ─► rows ─► LLM explains
```

See [`text_to_sql.py`](text_to_sql.py). The LLM only ever sees the schema, never trusted blindly:

```text
PASS  allowed : SELECT name FROM customers LIMIT 50
PASS  blocked (multiple statements): SELECT * FROM orders; DROP TABLE orders
PASS  blocked (must start with SELECT/WITH): DELETE FROM customers
PASS  blocked (comments not allowed): SELECT 1 -- ' OR 1=1
```

And even if validation had a hole, the **database** refuses (real run):

```text
blocked by DB: cannot execute UPDATE in a read-only transaction
```

**Defence layers:** schema-only prompt → validator → read-only role ([10](../10-database-security/)) → `statement_timeout` → `LIMIT`.

> ⚠️ **Common mistakes:** giving the LLM a superuser connection · executing whatever it returns · sending the whole database (not just the schema) in the prompt · no row limit.

## 3. SQL agents

A **SQL agent** is Text-to-SQL in a loop:

```text
  ┌──────────────────────────────────────────────┐
  ▼                                              │
Question → LLM: "which tables do I need?" → inspect schema → write SQL → run
                                                   │ error? → LLM reads error → fix SQL ─┘
                                                   ▼ success
                                              final answer
```
Tools it needs: `list_tables()`, `describe_table(name)`, `run_select(sql)`. Same safety rules apply to each tool.

## 4. RAG — Retrieval-Augmented Generation

```text
Documents → Chunk → Embed → Vector DB                       (indexing, done once)
Question  → Embed → Top-k similar chunks → Prompt → LLM     (every question)
```
Hands-on: [09 Part D](../09-vector-databases/), [Project 7](../11-database-engineering-projects/07-chroma-rag-search/).

## 5. Metadata filtering

Pure similarity can return the right *topic* from the wrong *user/year/department*. Filter first:

```python
col.query(query_texts=[q], n_results=3, where={"user": "ayesha"})                 # privacy boundary
col.query(query_texts=[q], n_results=3, where={"$and": [{"year": 2024}, {"dept": "legal"}]})
```
Metadata filters are also a **security feature**: they stop one user's memories leaking into another's answer.

## 6. FAISS vs Chroma vs pgvector for retrieval

| | FAISS | Chroma | pgvector (PostgreSQL extension) |
|---|---|---|---|
| Is | library | vector DB | vector type inside Postgres |
| Metadata + SQL joins | ❌ manual | filters only | ✅ full SQL |
| One system to run | ✅ (in-process) | ✅ | ✅ (you already have Postgres) |
| Scale / ANN tuning | ⭐ | good | good (HNSW/IVF indexes) |
| Choose when | max speed / research | quick RAG prototypes | vectors live next to relational data |

### pgvector — concept *(not run in my sandbox; standard pgvector syntax)*

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id SERIAL PRIMARY KEY, doc_id INT REFERENCES documents(id),
                     content TEXT, embedding vector(384));
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

-- top-3 most similar chunks, with a normal SQL filter and join
SELECT c.content, d.title, 1 - (c.embedding <=> $1) AS similarity
FROM chunks c JOIN documents d ON d.id = c.doc_id
WHERE d.dept = 'legal'
ORDER BY c.embedding <=> $1 LIMIT 3;          -- <=> is cosine distance
```
The attraction: **one database, one transaction, one backup** for both structured rows and vectors.

## 7. Agent memory

```text
Short-term memory  = the last N messages          → PostgreSQL   (exact, ordered)
Long-term memory   = facts worth keeping forever  → Chroma       (found by meaning)
```

[`agent_memory.py`](agent_memory.py) (real run) — the prompt the LLM would receive:

```text
Things I remember about ayesha:
- Ayesha is studying database engineering and prefers PostgreSQL.
- Ayesha is allergic to peanuts.

Recent conversation:
user: Hi!
assistant: Hello Ayesha, how can I help?

user: Which database should I use for my study project?
```
Bilal's memory about MongoDB was **not** retrieved — the `where={"user": ...}` filter kept it out.

Design questions I now ask for any agent:

| Question | Answer |
|---|---|
| What must be remembered *exactly*? | PostgreSQL rows |
| What must be remembered *by meaning*? | vector store |
| What may be forgotten? | TTL / delete old memories |
| Whose memory is it? | always store + filter by `user_id` |
| What may the agent write? | least-privilege DB role |

## 8. Database-backed AI agent (full picture)

```text
User ─► Agent ─► Redis cache?  ──hit──► answer
          │ miss
          ├─► PostgreSQL  (facts, orders, users, chat log)
          ├─► Chroma      (docs + long-term memory)
          ├─► MongoDB     (flexible event/chat logs)
          ▼
        LLM ─► answer ─► cache + log
```
That's exactly [Project 8](../11-database-engineering-projects/08-ai-database-backend/).

## ✏️ Practice

1. Add a table `refund_policy` to `shop` and ask Text-to-SQL "How many refunds this month?" — what could go wrong?
2. Extend `agent_memory.py`: add a TTL-style cleanup that deletes memories older than 30 days (store a timestamp in metadata).
3. Rewrite Project 7 retrieval with pgvector instead of Chroma. What got simpler? What got harder?
4. Design an agent for a university: which data goes in PostgreSQL, which in Chroma?

🎓 **You made it.** Back to the [README](../README.md) to tick off the checklist.
