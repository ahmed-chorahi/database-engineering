# 01b · INSERT, UPDATE, DELETE

Changing data. Always run these inside a transaction while learning, so you can undo mistakes.

```sql
BEGIN;
INSERT INTO customers (name, email, city) VALUES ('Test User', 't@mail.com', 'Quetta');
UPDATE customers SET city = 'Peshawar' WHERE name = 'Test User';
SELECT id, name, city FROM customers WHERE name = 'Test User';
DELETE FROM customers WHERE name = 'Test User';
ROLLBACK;   -- nothing was saved
```

```text
BEGIN
INSERT 0 1
UPDATE 1
 id |    name   |    city
----+-----------+----------
  7 | Test User | Peshawar
(1 row)

DELETE 1
ROLLBACK
```

**Why it works:** each command reports how many rows it touched (`UPDATE 1`). `ROLLBACK` throws all of it away.

> ⚠️ **Common mistake:** `UPDATE` or `DELETE` **without `WHERE`** hits every row. Run it as a `SELECT` with the same `WHERE` first.

**RETURNING** (PostgreSQL special) gives you the changed row back:

```sql
INSERT INTO products (name, category, price) VALUES ('Mouse','Electronics',25) RETURNING id, name;
```

✏️ **Try it:** raise all Stationery prices by 10% inside a transaction, check, then roll back.
