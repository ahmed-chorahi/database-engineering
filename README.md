<h1 align="center">🗄️ database-engineering</h1>

<p align="center">
  <i>My step-by-step journey from "what is a table?" to databases powering AI agents.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/FAISS-0467DF?logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/Chroma-FF6446" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" />
</p>

---

## 📖 What is this repository?

A **personal learning repo**. I'm a BS Computer Science student, and I'm learning database engineering from the ground up — one concept, one small example, one real output at a time.

It is **not** a textbook. Every topic is short, runnable, and written so I can revise it the night before an exam or interview.

## 💡 Why I created it

- Database courses felt like disconnected topics: SQL here, normalization there, "NoSQL" somewhere else.
- AI apps need **databases** (memory, retrieval, facts), but few resources connect the two.
- Writing things down with real queries and real output is the best way I know to actually understand them.

## 🎯 What I'm learning

```text
I learned databases → learned PostgreSQL → became comfortable with SQL → learned database design
→ learned transactions → learned optimization → learned NoSQL → understood distributed databases
→ learned vectors → practiced FAISS → learned Chroma → connected databases with AI
```

## 🗺️ Roadmap

```text
00 Prerequisites ─► 01 Fundamentals ─► 02 Relational DBs ─► 03 SQL ─► 04 Design
                                                                          │
12 AI + DB ◄─ 11 Projects ◄─ 10 Security ◄─ 09 Vectors ◄─ 08 Distributed ◄─ 07 NoSQL ◄─ 06 Indexing ◄─ 05 Transactions
```

| # | Folder | What's inside |
|---|---|---|
| 00 | [prerequisites](00-prerequisites/) | data, tables, keys, CRUD — the vocabulary |
| 01 | [database-fundamentals](01-database-fundamentals/) | DBMS, ACID, CAP, OLTP/OLAP, backups |
| 02 | [relational-databases](02-relational-databases/) | PostgreSQL + psql, constraints, relationships, views, triggers |
| 03 | [sql-postgresql](03-sql-postgresql/) ⭐ | SQL from `SELECT` to window functions on a practice DB |
| 04 | [database-design](04-database-design/) | ER diagrams, 1NF → 3NF |
| 05 | [transactions-concurrency](05-transactions-concurrency/) | isolation, locks, deadlocks |
| 06 | [indexing-query-performance](06-indexing-query-performance/) | `EXPLAIN ANALYZE`, indexes, N+1 |
| 07 | [nosql](07-nosql/) | MongoDB + Redis |
| 08 | [distributed-databases](08-distributed-databases/) | replication, sharding, CAP |
| 09 | [vector-databases](09-vector-databases/) ⭐ | embeddings, FAISS, Chroma, semantic search |
| 10 | [database-security](10-database-security/) | roles, SQL injection, secrets |
| 11 | [database-engineering-projects](11-database-engineering-projects/) | 8 projects |
| 12 | [ai-database-integration](12-ai-database-integration/) | text-to-SQL, RAG, agent memory |

Also: [ROADMAP.md](ROADMAP.md) (visual path) · [CONNECTIONS.md](CONNECTIONS.md) (concept map + connection strings)

## 🛠️ Technologies

| Tool | Used for |
|---|---|
| **PostgreSQL + psql** | SQL, relational design, transactions, indexing |
| **MongoDB** | document / NoSQL modelling |
| **Redis** | key-value store, caching |
| **FAISS** | fast vector similarity search |
| **Chroma** | vector database, RAG |
| **Python** (NumPy, psycopg2, pymongo, redis) | integrations and AI examples |

## 🚀 Quick start

```bash
git clone https://github.com/<your-username>/database-engineering.git
cd database-engineering
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# PostgreSQL practice database
psql -U postgres -f 03-sql-postgresql/practice-db/schema.sql
psql -U postgres -f 03-sql-postgresql/practice-db/seed.sql
psql -U postgres -d shop
```

## 🐘 PostgreSQL / SQL

The biggest part of the repo. Each lesson is:

```text
Problem → SQL Query → Expected Output → Short Explanation
```

```sql
-- Customers who never ordered
SELECT name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```
```text
    name
-------------
 Zainab Noor
 Usman Tariq
```

Outputs in the SQL lessons come from real `psql` runs against the practice database. Topics: filtering, aggregates, joins, subqueries, set operations, CTEs (incl. recursive), window functions, transactions.

## 🍃 NoSQL

[MongoDB](07-nosql/mongodb.md): documents, CRUD, embedding vs referencing, aggregation pipeline.
[Redis](07-nosql/redis.md): strings, lists, sets, hashes, TTL, cache-aside.

> My rule: start with PostgreSQL; use NoSQL when a *specific* problem calls for it.

## ⚡ FAISS

A library that finds the nearest vectors fast. It only stores vectors — metadata is your job.

```python
index = faiss.IndexFlatL2(d); index.add(vectors)
D, I = index.search(query, 3)          # distances, row ids
```

## 🎨 Chroma

A vector **database**: vectors + documents + metadata + persistence.

```python
col.add(ids=["n1"], documents=["Redis is a cache"], metadatas=[{"topic": "nosql"}])
col.query(query_texts=["fast storage"], n_results=2, where={"topic": "nosql"})
```

```text
FAISS  = fast vector search library       (the engine)
Chroma = vector database for RAG apps     (the whole car)
```

## ⚖️ SQL vs NoSQL vs Vector

| | SQL (PostgreSQL) | NoSQL (MongoDB / Redis) | Vector (FAISS / Chroma) |
|---|---|---|---|
| Data | tables, rows | documents / key-value | embeddings |
| Question it answers | "which rows match this condition?" | "get this record / key" | "what is *similar* to this?" |
| Schema | strict | flexible / none | vectors + metadata |
| Strength | integrity, joins, ACID | flexibility, speed | semantic search, RAG |
| Weakness | rigid, scaling writes | weaker joins/integrity | approximate, not exact |
| Example | orders, payments | blog posts, sessions | "find docs about refunds" |

## 🧪 Projects

| # | Project | Highlight (from my runs) |
|---|---|---|
| 1 | [Student Management](11-database-engineering-projects/01-student-management/) | relationships + CRUD |
| 2 | [E-Commerce](11-database-engineering-projects/02-ecommerce-database/) | one index: **6.3 ms → 0.11 ms** |
| 3 | [Banking Transactions](11-database-engineering-projects/03-banking-transactions/) | 800 concurrent transfers, money conserved |
| 4 | [MongoDB App](11-database-engineering-projects/04-mongodb-app/) | embedding + aggregation |
| 5 | [Redis Caching](11-database-engineering-projects/05-redis-caching/) | **77 ms → 0.06 ms** with cache-aside |
| 6 | [FAISS Semantic Search](11-database-engineering-projects/06-faiss-semantic-search/) | chunk → embed → top-k |
| 7 | [Chroma RAG](11-database-engineering-projects/07-chroma-rag-search/) | metadata filters + grounded prompt |
| 8 | [AI Database Backend](11-database-engineering-projects/08-ai-database-backend/) | PostgreSQL + Mongo + Redis + Chroma + LLM |

## ✅ Learning progress

- [x] 00 Prerequisites
- [x] 01 Database fundamentals
- [x] 02 Relational databases (PostgreSQL)
- [x] 03 SQL
- [x] 04 Database design
- [x] 05 Transactions & concurrency
- [x] 06 Indexing & performance
- [x] 07 NoSQL (MongoDB, Redis)
- [x] 08 Distributed databases
- [x] 09 Vector databases (FAISS, Chroma)
- [x] 10 Database security
- [x] 11 Projects 1–8
- [x] 12 AI + database integration
- [ ] Next: try pgvector for real, add a SQL agent with tool-calling, learn Cassandra/graph DBs

## 🤖 AI ↔ database connection

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

LLMs are great readers with poor memory. **SQL gives them exact facts, vector search gives them relevant context, Redis makes it fast, and security keeps it safe.** Details in [12 · AI + Database Integration](12-ai-database-integration/).

## 📝 A note on the examples

- SQL outputs, index timings, the concurrency/deadlock demo, Redis cache timings, FAISS and Chroma outputs were produced by actually running the code.
- Vector outputs use a small **offline fallback embedder** (`embed.py`) so everything runs without downloads; install `sentence-transformers` to get real semantic matching.
- MongoDB examples and the pgvector snippet are written to standard syntax and are labelled where I did not run them.

---
<p align="center"><i>Learn it, run it, break it, write it down.</i></p>
