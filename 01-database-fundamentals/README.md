# 01 · Database Fundamentals

> The big picture before touching any tool.

## DBMS vs RDBMS

- **DBMS** – any software that manages data (even a file-based one).
- **RDBMS** – a DBMS that stores data in **related tables** and uses **SQL** (PostgreSQL, MySQL).

## Relational vs NoSQL vs Vector

```text
Relational          Document (NoSQL)        Key-Value (NoSQL)     Vector
┌────┬──────┐       { "name": "Ayesha",      "user:1" → "Ayesha"   [0.12, -0.8, 0.33, ...]
│ id │ name │         "skills": ["sql"] }    "session:9" → {...}    "find things that
└────┴──────┘                                                       MEAN the same"
fixed columns       flexible JSON           lookup by key, fast   similarity search
```

| | Relational | Document | Key-Value | Vector |
|---|---|---|---|---|
| Example | PostgreSQL | MongoDB | Redis | FAISS, Chroma |
| Best at | structured data, joins, consistency | flexible nested data | caching, sessions | semantic search, RAG |
| Query by | SQL | JSON filters | key | nearest neighbour |

## Schema, Constraints, Data types

- **Schema** – the blueprint (see [00](../00-prerequisites/)).
- **Data types** – what a column may hold: `INT`, `TEXT`, `NUMERIC`, `DATE`, `BOOLEAN`, `JSONB`.
- **Constraints** – rules the database enforces *for you*:

| Constraint | Rule |
|---|---|
| `PRIMARY KEY` | unique + not null identifier |
| `FOREIGN KEY` | must point to an existing row |
| `UNIQUE` | no duplicates |
| `NOT NULL` | value required |
| `CHECK` | custom rule, e.g. `price > 0` |
| `DEFAULT` | value if none given |

> **Why:** bad data blocked at the door is easier than bad data cleaned later.

## ACID

The four promises of a reliable transaction:

| | Meaning | Bank-transfer example |
|---|---|---|
| **A**tomicity | all or nothing | debit *and* credit happen, or neither |
| **C**onsistency | rules always hold | balance never goes below 0 |
| **I**solation | transactions don't see each other's half-done work | two transfers don't corrupt each other |
| **D**urability | committed = survives a crash | power cut after "success" doesn't lose it |

## CAP theorem (intuition)

In a distributed system, when the network breaks you can only keep **one** of:

```text
        Consistency
           /\
          /  \
         / ?? \          pick 2 — but partitions
        /______\         WILL happen, so really:
 Availability──Partition   C or A during a failure
                Tolerance
```

- **CP**: refuse to answer rather than give wrong data (banks).
- **AP**: always answer, maybe slightly stale (social feeds).

More in [08 · Distributed Databases](../08-distributed-databases/).

## OLTP vs OLAP

| | OLTP | OLAP |
|---|---|---|
| Purpose | run the business | analyse the business |
| Queries | many small reads/writes | few huge aggregations |
| Example | "place order #55" | "sales per region per year" |
| Design | normalised | denormalised / columnar |

## Backup & recovery

| Type | What | Postgres tool |
|---|---|---|
| Logical | export SQL | `pg_dump` / `pg_restore` |
| Physical | copy data files | `pg_basebackup` |
| Point-in-time | replay the WAL log to a moment | WAL archiving |

```bash
pg_dump -U postgres -d shop -f shop_backup.sql      # backup
createdb -U postgres shop_restored
psql -U postgres -d shop_restored -f shop_backup.sql # restore
```

> ⚠️ **Mistake:** never testing the restore. A backup you've never restored is a hope, not a backup.

## Architecture basics

```text
 Client ──► Connection ──► Parser ──► Planner/Optimizer ──► Executor ──► Storage
 (psql)     handler        (SQL→tree)  (picks fastest plan)  (runs it)    (disk + cache)
                                                                  │
                                                          WAL (write-ahead log)
                                                          = durability + recovery
```

The key idea: you say **what** you want (SQL), the optimizer decides **how**.

## ✏️ Practice

1. Which ACID letter stops a half-finished transfer?
2. Is a "likes counter" CP or AP? Defend it.
3. Run `pg_dump` on any database and open the file.

➡️ Next: [02 · Relational Databases](../02-relational-databases/)
