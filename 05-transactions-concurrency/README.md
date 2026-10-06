# 05 · Transactions & Concurrency

> What happens when many people touch the same data at the same time.

Files: [`setup.sql`](setup.sql) (bank, seats, stock tables) · [`concurrency_demo.py`](concurrency_demo.py) (two sessions in Python — outputs below came from it).

## 1. Transaction basics

**What:** a group of statements treated as one unit. **Why:** a bank transfer is two updates; a crash between them must not lose money.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;   -- debit
UPDATE accounts SET balance = balance + 100 WHERE id = 2;   -- credit
COMMIT;                                                      -- or ROLLBACK;
```

ACID refresher → [01](../01-database-fundamentals/). In PostgreSQL every statement is already atomic; `BEGIN` extends that to several statements.

### SAVEPOINT — a checkpoint inside a transaction

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
SAVEPOINT after_debit;
UPDATE accounts SET balance = balance + 9999 WHERE id = 99;  -- oops, wrong id (0 rows)
ROLLBACK TO after_debit;                                     -- undo only the oops
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```
```text
 id | owner  | balance
----+--------+---------
  1 | Ayesha |  900.00
  2 | Bilal  |  600.00
```

> ⚠️ **Common mistake:** assuming `UPDATE ... WHERE id = 99` raises an error. It quietly updates **0 rows**. Always check the row count.

## 2. The three bad things that can happen

| Anomaly | Story |
|---|---|
| **Dirty read** | I read data another transaction hasn't committed (and may roll back) |
| **Non-repeatable read** | I read a row twice in one transaction and it changed in between |
| **Phantom read** | I run the same query twice and new *rows* appear |

```text
Time ─►
Session A:  BEGIN; SELECT balance → 1000 ........................ SELECT balance → 1050 (?!)
Session B:                      UPDATE +50; COMMIT
                                          └── non-repeatable read
```

## 3. Isolation levels

| Level | Dirty | Non-repeatable | Phantom |
|---|---|---|---|
| READ UNCOMMITTED* | no | possible | possible |
| **READ COMMITTED** (Postgres default) | no | possible | possible |
| REPEATABLE READ | no | no | no (in Postgres) |
| SERIALIZABLE | no | no | no |

\*PostgreSQL treats it as READ COMMITTED — dirty reads never happen.

Real output from `concurrency_demo.py` (read a balance, another session adds 50 and commits, read again):

```text
READ COMMITTED  : (1000.00, 1050.00)    ← changed under my feet
REPEATABLE READ : (1000.00, 1000.00)    ← I keep my snapshot
```

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
```

**Use when:** READ COMMITTED for most apps; REPEATABLE READ for reports that must see one consistent snapshot; SERIALIZABLE when correctness beats speed (be ready to **retry** on serialization errors).

## 4. Locks

PostgreSQL uses **MVCC**: readers don't block writers. Writers block *other writers of the same row*.

| Lock | How | Use |
|---|---|---|
| Row-level | `UPDATE`, or `SELECT ... FOR UPDATE` | protect a row you're about to change |
| Table-level | `LOCK TABLE` / DDL | rare, heavy |

```text
Session A: BEGIN; UPDATE accounts SET balance = balance - 100 WHERE id = 1;   -- holds row lock
Session B: UPDATE accounts SET balance = balance - 50 WHERE id = 1;           -- ...waits...
Session A: COMMIT;                                                            -- B continues now
```

## 5. Example 1 — Bank transfer (race condition)

Wrong (read in the app, write back later):

```text
A reads 1000   B reads 1000
A writes 900   B writes 950    ← A's debit is lost!
```

Right — let the database do the arithmetic atomically:

```sql
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
```

Or lock first when you need to check rules:

```sql
BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;   -- others wait here
-- check balance >= amount in your code
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

## 6. Example 2 — Ticket booking (don't sell a seat twice)

```sql
-- only one concurrent buyer can win: the WHERE clause is the guard
UPDATE seats SET booked_by = 'Ayesha'
WHERE seat_no = 1 AND booked_by IS NULL;
```
```text
UPDATE 1   ← got it
UPDATE 0   ← someone else already did (tell the user)
```

For "grab any free seat" with many workers: `SELECT ... FOR UPDATE SKIP LOCKED LIMIT 1`.

## 7. Example 3 — Inventory

```sql
UPDATE stock SET qty = qty - 1 WHERE product = 'Laptop';
```

With `CHECK (qty >= 0)` the second buyer of the last laptop gets:

```text
ERROR:  new row for relation "stock" violates check constraint "stock_qty_check"
```

The constraint is the safety net even if the app forgets to check.

## 8. Deadlocks

```text
T1: locks account 1 ─────► wants account 2 ┐
                                           ├─ each waits for the other forever
T2: locks account 2 ─────► wants account 1 ┘
```

PostgreSQL detects it and kills one transaction. From the demo:

```text
{'T1 (1 then 2)': 'DEADLOCK -> rolled back', 'T2 (2 then 1)': 'committed'}
```
(Which one dies varies run to run.)

```text
ERROR:  deadlock detected
```

**Fix:** always lock rows in the **same order** (e.g. lowest id first), keep transactions short, retry the victim.

## 9. Concurrency control cheat sheet

| Approach | Idea | Postgres |
|---|---|---|
| Pessimistic | lock first, then work | `SELECT ... FOR UPDATE` |
| Optimistic | work, then check nothing changed | `UPDATE ... WHERE version = 7` |
| MVCC | keep old row versions so readers never wait | built in |

## ✏️ Practice

1. Open two `psql` windows and reproduce the lost update. Then fix it with `FOR UPDATE`.
2. Make seat booking safe for 10 threads in Python (use `concurrency_demo.py` as a base).
3. Force a deadlock in two psql windows, then prevent it with lock ordering.

➡️ Next: [06 · Indexing & Query Performance](../06-indexing-query-performance/)
