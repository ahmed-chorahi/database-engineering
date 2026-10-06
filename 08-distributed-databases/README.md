# 08 · Distributed Databases

> One server isn't enough when you need more speed, more storage, or no downtime. This section is mostly pictures.

## 1. Scaling

```text
VERTICAL (scale up)              HORIZONTAL (scale out)
┌───────────────┐                ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│  BIGGER       │                │ DB  │ │ DB  │ │ DB  │ │ DB  │
│  SERVER       │                └─────┘ └─────┘ └─────┘ └─────┘
│  (more RAM/CPU)│                 many small servers
└───────────────┘
simple, but has a ceiling         no ceiling, but complex
```

**My rule:** scale vertically first, add indexes/caching, *then* go horizontal.

## 2. Replication — copies for safety and read speed

```text
              writes
 App ───────────────────► PRIMARY ──── replicates ────┬──► REPLICA 1
  │                                                    └──► REPLICA 2
  └──── reads (can go to replicas) ◄──────────────────────────┘
```

| Term | Meaning |
|---|---|
| **Primary** (leader) | accepts writes |
| **Replica** (follower) | copy that stays in sync |
| **Read replica** | replica used only to serve `SELECT`s → more read capacity |
| **Failover** | promote a replica when the primary dies |

| Sync | Async |
|---|---|
| primary waits for replica | primary doesn't wait |
| no data loss | tiny chance of losing last writes |
| slower writes | faster writes, **replica lag** |

PostgreSQL does this with streaming replication (WAL shipping).

> ⚠️ **Common mistake:** writing then immediately reading from a replica and not seeing your own write (replica lag).

## 3. Partitioning vs Sharding

```text
PARTITIONING (one server, one table split up)     SHARDING (many servers)
orders                                            Shard A: users 1–1M
 ├─ orders_2024_q1                                Shard B: users 1M–2M
 ├─ orders_2024_q2                                Shard C: users 2M–3M
 └─ orders_2024_q3                                (each shard is its own DB server)
```

```sql
-- PostgreSQL native partitioning
CREATE TABLE logs (id BIGSERIAL, created DATE NOT NULL, msg TEXT) PARTITION BY RANGE (created);
CREATE TABLE logs_2024 PARTITION OF logs FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

| Shard by | Good | Bad |
|---|---|---|
| range (id 1–1M) | easy range queries | hot spot on the newest shard |
| hash (`hash(id) % N`) | even spread | range queries hit all shards |
| geography | low latency | uneven sizes |

Sharding makes joins and transactions **across** shards painful — it's a last resort.

## 4. Consistency & availability

- **Strong consistency:** after a write, every read sees it. Simple to reason about, slower.
- **Eventual consistency:** replicas catch up *eventually*. Fast and available, but reads may be briefly stale.

### CAP theorem (again, with a story)

```text
Network cable between two data centres is cut (Partition).
Ayesha writes in DC-1. Bilal reads in DC-2.

  CP: DC-2 says "can't answer right now"      → consistent, less available
  AP: DC-2 answers with old data              → available, maybe inconsistent
```

| Type | Behaviour | Examples |
|---|---|---|
| CP | refuses when unsure | banking ledgers, etcd, MongoDB (default settings) |
| AP | always answers | Cassandra, DynamoDB (default) , caches |

## 5. Distributed transactions

Updating two databases atomically is hard.

```text
Two-Phase Commit (2PC)
 Coordinator: "Can everyone commit?"  ─► A: yes   B: yes
 Coordinator: "COMMIT"                ─► A: done  B: done
 (if anyone says no → everyone ROLLBACK)
```

Downside: blocking and slow if the coordinator dies. Modern alternative: the **Saga pattern** — a chain of local transactions, each with a *compensating action* (refund, un-reserve) if a later step fails.

```text
Reserve stock ─► Charge card ─► Create shipment
      ▲               │ fails
      └── undo ◄──────┘  (compensate: release stock)
```

## 6. Fault tolerance

| Threat | Defence |
|---|---|
| server dies | replicas + automatic failover |
| disk dies | RAID, backups, WAL archiving |
| data centre dies | multi-region replicas |
| bad deploy deletes data | point-in-time recovery |
| network split | quorum (majority) decisions |

Metrics worth knowing: **RPO** (how much data can I lose?) and **RTO** (how long can I be down?).

## 7. Putting it together

```text
                    Load balancer
                          │
                     ┌────┴─────┐
         writes ────►  PRIMARY  ─── replicates ──► REPLICA A ◄── reads
                     └──────────┘            └───► REPLICA B ◄── reads
                          │
                       backups + WAL archive
```

## ✏️ Practice

1. Draw the architecture for a site with 100× more reads than writes.
2. You shard users by `id % 3`. Add a 4th shard — what breaks? (Look up *consistent hashing*.)
3. Is a payment system CP or AP? Is a "post likes" counter?

➡️ Next: [09 · Vector Databases](../09-vector-databases/)
