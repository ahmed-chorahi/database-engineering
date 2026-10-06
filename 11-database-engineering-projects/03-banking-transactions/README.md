# Project 3 — Banking Transaction System

**Databases:** PostgreSQL · **Files:** [`schema.sql`](schema.sql) · [`transfer.py`](transfer.py)

## Problem
Move money between accounts while many clients do it at once, without ever creating or destroying money.

## Requirements
- A transfer is atomic: debit + credit + log entry, or nothing.
- No overdrafts. No lost updates. No deadlocks.
- Total money in the system never changes.

## Choose database
**PostgreSQL** — full ACID, row locks, `CHECK` constraints.

## Design
```text
accounts(id, owner, balance CHECK >= 0)
transfers(id, from_acct, to_acct, amount CHECK > 0, created_at)   ← audit trail
```

## Implementation — the key function
```python
cur.execute("SELECT id FROM accounts WHERE id IN (%s,%s) ORDER BY id FOR UPDATE", (first, second))  # lock in id order
cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, src))              # CHECK blocks overdraft
cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, dst))
cur.execute("INSERT INTO transfers ...")
conn.commit()                                   # on CheckViolation: conn.rollback()
```
| Problem | Defence |
|---|---|
| half a transfer | transaction (`commit` / `rollback`) |
| overdraft | `CHECK (balance >= 0)` |
| lost update | database does `balance = balance - x`, plus `FOR UPDATE` |
| deadlock | always lock rows in **id order** |

## Testing — stress test (real run)
8 threads × 100 random transfers between 5 accounts:
```bash
psql -U postgres -f schema.sql && python transfer.py
```
```text
total money before: 5000.00
transfers: {'ok': 655, 'rejected': 145}
total money after : 5000.00
negative balances: 0
```
145 transfers were correctly **rejected** for insufficient funds; money is conserved.

## Performance
Row locks only block transfers touching the *same* accounts. Try changing 5 accounts to 5,000 and watch throughput.

## What I learned
- The invariant ("total is constant") makes a perfect concurrency test.
- Constraints are the last line of defence even when app code is correct.
- Consistent lock ordering removes deadlocks instead of handling them.
