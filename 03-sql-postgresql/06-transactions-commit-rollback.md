# 06 · Transactions: COMMIT & ROLLBACK

A transaction groups statements into one unit: **all succeed or none do.** (Deep dive in [05](../05-transactions-concurrency/).)

```text
BEGIN ──► statements ──┬─► COMMIT   (save everything)
                       └─► ROLLBACK (undo everything)
```

### ROLLBACK

**Problem:** Double Stationery prices, look at the result, then change my mind.

```sql
BEGIN;
UPDATE products SET price = price * 2 WHERE category = 'Stationery';
SELECT name, price FROM products WHERE category = 'Stationery';
ROLLBACK;
SELECT name, price FROM products WHERE category = 'Stationery';
```

```text
-- inside the transaction
   name   | price
----------+-------
 Notebook |  7.00
 Pen Pack | 10.00

-- after ROLLBACK
   name   | price
----------+-------
 Notebook |  3.50
 Pen Pack |  5.00
```

**Why it works:** changes live in a private workspace until `COMMIT`.

### COMMIT

```sql
BEGIN;
UPDATE orders SET status = 'shipped' WHERE id = 6;
COMMIT;
```

Now it's permanent and visible to everyone.

> ⚠️ **Common mistake:** leaving a transaction open (`BEGIN` with no `COMMIT`). It can hold locks and block others.

> 💡 psql runs in **autocommit** mode: each statement outside `BEGIN` commits immediately.

✏️ **Try it:** inside a transaction, `DELETE FROM order_items;` — count the rows, then `ROLLBACK` and count again. (Thank me later.)
