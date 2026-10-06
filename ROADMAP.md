# 🗺️ Roadmap

The order I learned things in — and why each step needs the one before it.

```text
Database Basics            (00, 01)   what is a database, tables, keys, ACID, CAP
      ↓
PostgreSQL                 (02)       install, psql, schemas, constraints, relationships
      ↓
SQL                        (03)       SELECT → JOIN → CTE → window functions
      ↓
Database Design            (04)       entities, ER diagrams, normalization
      ↓
Transactions               (05)       ACID in practice, isolation, locks, deadlocks
      ↓
Indexes & Performance      (06)       EXPLAIN ANALYZE, B-tree, composite, partial
      ↓
NoSQL                      (07)       MongoDB documents, Redis caching
      ↓
Distributed Databases      (08)       replication, sharding, CAP, consistency
      ↓
Vector Fundamentals        (09 A)     embeddings, cosine, nearest neighbour
      ↓
FAISS                      (09 B)     fast vector search library
      ↓
Chroma                     (09 C)     vector database with metadata
      ↓
Semantic Search            (09 D)     chunk → embed → index → top-k
      ↓
RAG                        (07, 12)   retrieve chunks → ground an LLM answer
      ↓
AI Agents + Databases      (12)       text-to-SQL, memory, database-backed agents
```

## Why this order?

| Step | Needs from before |
|---|---|
| SQL | tables, keys, a running PostgreSQL |
| Design | knowing what joins feel like |
| Transactions | tables worth protecting |
| Indexes | queries slow enough to care about |
| NoSQL | knowing what SQL *can't* do comfortably |
| Distributed | a single-server mental model first |
| Vectors | the idea that "a database answers questions" — now by *similarity* |
| AI agents | SQL for facts + vectors for meaning + security for safety |

## Suggested time plan

| Week | Topics | Output |
|---|---|---|
| 1 | 00, 01, 02 | PostgreSQL running, `school` DB |
| 2–3 | 03 | all SQL lessons done, Project 1 |
| 4 | 04 | redesign something messy into 3NF |
| 5 | 05, 06 | Projects 2 and 3 |
| 6 | 07, 08 | Projects 4 and 5 |
| 7–8 | 09 | Projects 6 and 7 |
| 9 | 10, 12 | secure the app, Project 8 |

## Milestones

- 🟢 **Beginner done:** can design tables and write joins.
- 🟡 **Intermediate done:** can explain a query plan and fix a slow query.
- 🔴 **Advanced done:** can pick the right database for a problem and defend it.
