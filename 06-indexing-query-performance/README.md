# 06 · Indexing & Query Performance

> The most "wow" section for me: same query, 36 ms → 0.13 ms, just by adding one index.

Run [`setup.sql`](setup.sql) first — it builds a `perf` database with **500,000 rows**. (All numbers below are from my real run; yours will differ but the *shape* will match.)

## 1. Why indexes exist

**Analogy:** the index at the back of a textbook. Without it you read every page; with it you jump straight to page 212.

```text
Without index:  scan row 1, row 2, row 3 ... row 500,000      (Sequential Scan)
With B-tree:          [root]
                     /  |   \
                [..]  [..]  [..]   ← a few hops to the right leaf    (Index Scan)
```

## 2. The workflow

```text
Slow Query ─► EXPLAIN ANALYZE ─► Find Bottleneck ─► Create/Fix Index ─► Run Again ─► Compare
```

### Step 1 — Slow query + EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE SELECT * FROM big_orders WHERE customer_id = 4242;
```
```text
 Gather  (cost=1000.00..7127.27 rows=11 width=25) (actual time=5.698..36.324 rows=9 loops=1)
   Workers Planned: 2
   ->  Parallel Seq Scan on big_orders  (cost=0.00..6126.17 rows=5 width=25)
         Filter: (customer_id = 4242)
         Rows Removed by Filter: 166664
 Planning Time: 0.249 ms
 Execution Time: 36.364 ms
```

### Step 2 — Bottleneck

`Seq Scan` + `Rows Removed by Filter: 166664` (per worker) = it read the whole table to return **9 rows**.

### Step 3 — Create the index

```sql
CREATE INDEX idx_big_orders_customer ON big_orders (customer_id);
```

### Step 4 — Run again

```text
 Bitmap Heap Scan on big_orders  (cost=4.51..46.80 rows=11 width=25) (actual time=0.038..0.081 rows=9 loops=1)
   Recheck Cond: (customer_id = 4242)
   ->  Bitmap Index Scan on idx_big_orders_customer  (actual time=0.029..0.029 rows=9 loops=1)
 Execution Time: 0.127 ms
```

### Step 5 — Compare

| | Plan | Time |
|---|---|---|
| Before | Parallel Seq Scan | **36.4 ms** |
| After | Bitmap Index Scan | **0.13 ms** (~280× faster) |

> 💡 PostgreSQL chose a *Bitmap* scan, not a plain *Index Scan*. Both use the index; bitmap is picked when several rows are fetched. Don't panic — it's still the index doing the work.

### Reading EXPLAIN

| Term | Meaning |
|---|---|
| `cost=a..b` | planner's estimate (unit-less) |
| `rows=` | estimated rows (compare with `actual rows`!) |
| `actual time` | real milliseconds |
| `Seq Scan` | read the whole table |
| `Index Scan` / `Bitmap Index Scan` | use an index |
| `EXPLAIN` | only plan · `EXPLAIN ANALYZE` | plan **and runs it** |

> ⚠️ `EXPLAIN ANALYZE` on `UPDATE`/`DELETE` really executes them. Wrap in `BEGIN; ... ROLLBACK;`.

## 3. Index types

| Type | Good for | Example |
|---|---|---|
| **B-tree** (default) | `=`, `<`, `>`, `BETWEEN`, `ORDER BY` | `CREATE INDEX ON t (col);` |
| **Hash** | only `=` | `CREATE INDEX ON t USING hash (col);` |
| **Composite** | filters on several columns | `CREATE INDEX ON t (status, created_at);` |
| **Unique** | enforce no duplicates (+ speed) | `CREATE UNIQUE INDEX ON users (email);` |
| **Partial** | index only some rows | `... WHERE status = 'pending'` |
| GIN / GiST | JSONB, full-text, arrays (extra reading) | |

### Composite index

```sql
EXPLAIN ANALYZE SELECT * FROM big_orders WHERE status='paid' AND created_at='2024-03-01';
-- before: Parallel Seq Scan, 46.8 ms
CREATE INDEX idx_status_date ON big_orders (status, created_at);
-- after:  Bitmap Index Scan, 0.75 ms
```

**Column order matters:** `(status, created_at)` helps filters on `status` or on `status + created_at`, but **not** on `created_at` alone (leftmost-prefix rule).

### Partial index

```sql
CREATE INDEX idx_pending ON big_orders (created_at) WHERE status = 'pending';
```
```text
 partial | full_idx
---------+----------
 608 kB  | 4552 kB       ← the partial index is ~7× smaller
```

**Use when:** you query a small slice (pending jobs, active users) again and again.

## 4. Index trade-offs

| ✅ Pros | ❌ Cons |
|---|---|
| faster reads | slower `INSERT/UPDATE/DELETE` (index must be updated) |
| enforce uniqueness | uses disk (`pg_relation_size`) |
| faster sorts/joins | too many indexes = confusion + slow writes |

When an index **won't** be used:

```sql
WHERE status = 'paid'            -- matches 1/3 of the table → planner may ignore the index
WHERE customer_id + 0 = 4242     -- expression on the column → Seq Scan (index can't be used)
```
```text
 Parallel Seq Scan on big_orders ... Filter: ((customer_id + 0) = 4242)
```

> ⚠️ **Common mistakes:** indexing every column · wrapping an indexed column in a function · not running `ANALYZE` after bulk loads.

## 5. Finding slow queries

```sql
-- enable once:  CREATE EXTENSION pg_stat_statements;  (+ add to shared_preload_libraries)
SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 5;
```

Other tools: `\timing` in psql, `log_min_duration_statement = 200` (log anything over 200 ms).

## 6. Query optimization checklist

1. `SELECT` only needed columns (not `*`).
2. `WHERE` columns indexed? Join columns (FKs!) indexed?
3. `LIMIT` for big result sets.
4. Don't wrap indexed columns in functions.
5. Check `rows=` estimate vs actual → run `ANALYZE`.
6. Read the plan, don't guess.

## 7. The N+1 problem

The most common performance bug in apps.

```python
# ❌ N+1: 1 query for orders + 1 query PER order for its customer
orders = db.query("SELECT * FROM orders")                      # 1 query
for o in orders:
    c = db.query("SELECT * FROM customers WHERE id = %s", o.customer_id)   # N queries

# ✅ one JOIN
rows = db.query("""SELECT o.id, c.name FROM orders o JOIN customers c ON c.id = o.customer_id""")
```

1,000 orders → 1,001 round trips vs **1**. Network latency is usually the real cost, not the SQL.

## ✏️ Practice

1. Run `EXPLAIN ANALYZE` on `WHERE amount > 990`. Add an index. Did it help? Why or why not?
2. Create the composite index in the *wrong* order and test a query on `created_at` only.
3. Measure insert time for 100k rows with 0 vs 4 indexes.

➡️ Next: [07 · NoSQL](../07-nosql/)
