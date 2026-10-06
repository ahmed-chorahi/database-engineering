# 11 · Database Engineering Projects

> Eight projects, each one a little harder, each reusing what came before.

Every project follows the same path:

```text
Problem → Requirements → Choose Database → Design → Implementation
        → Queries → Testing → Performance → What I Learned
```

| # | Project | Databases | Main skill |
|---|---|---|---|
| 1 | [Student Management](01-student-management/) | PostgreSQL | tables, relationships, CRUD, SQL |
| 2 | [E-Commerce Database](02-ecommerce-database/) | PostgreSQL | normalization, indexing |
| 3 | [Banking Transactions](03-banking-transactions/) | PostgreSQL | ACID, locks, concurrency |
| 4 | [MongoDB App](04-mongodb-app/) | MongoDB | document modeling, aggregation |
| 5 | [Redis Caching](05-redis-caching/) | PostgreSQL + Redis | cache-aside, TTL |
| 6 | [FAISS Semantic Search](06-faiss-semantic-search/) | FAISS | embeddings, top-k search |
| 7 | [Chroma RAG Search](07-chroma-rag-search/) | Chroma | chunking, metadata, retrieval |
| 8 | [AI Database Backend](08-ai-database-backend/) | PG + Mongo + Redis + Chroma | everything together |

> Output blocks marked **(real run)** were produced on PostgreSQL 16 / Redis 7 / Chroma. Timings change per machine; the *ratios* are what matter. MongoDB output is marked **(expected)** — worked out from the data by hand.
