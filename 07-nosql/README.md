# 07 · NoSQL

> Not "SQL is bad" — just "sometimes a different shape fits better."

| | [MongoDB](mongodb.md) | [Redis](redis.md) |
|---|---|---|
| Model | documents (JSON-like) | key → value, in memory |
| Think of it as | a folder of JSON files you can query | a super-fast dictionary |
| Great for | flexible, nested, changing data | caching, sessions, counters, queues |

## When does NoSQL make sense?

```text
Is the data highly relational with strict rules (money, orders)?   ──► PostgreSQL
Is each record a self-contained blob whose shape varies?           ──► MongoDB
Do I need sub-millisecond reads of data I can recompute?           ──► Redis (cache)
Do I need "find things that mean the same"?                        ──► Vector DB (09)
```

**My rule:** start with PostgreSQL. Reach for NoSQL when a *specific* problem asks for it. (Postgres even has `JSONB` for flexible fields.)

## SQL vs NoSQL at a glance

| | PostgreSQL | MongoDB | Redis |
|---|---|---|---|
| Schema | fixed, enforced | flexible | none |
| Relationships | joins + FKs | embed or reference | none |
| Transactions | strong ACID | supported, but design to avoid | limited (`MULTI`) |
| Scaling | vertical first, replicas | built-in sharding | clustering |
| Query language | SQL | JSON filters + pipeline | commands |

➡️ Start with [MongoDB](mongodb.md), then [Redis](redis.md). Next section: [08 · Distributed Databases](../08-distributed-databases/)
