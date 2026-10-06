# 03 · SQL + PostgreSQL

> The biggest section. I learn SQL by asking questions of one small shop database and checking the real output.

Every lesson follows:

```text
Problem
   ↓
SQL Query
   ↓
Expected Output   ← copied from a real psql run
   ↓
Short Explanation
```

## Set up the practice database (2 minutes)

```bash
cd practice-db
psql -U postgres -f schema.sql
psql -U postgres -f seed.sql
psql -U postgres -d shop        # you're in
```

```text
customers ──< orders ──< order_items >── products        employees ──┐
    1             1            N              1              ▲        │ manager_id
                                                             └────────┘ (self reference)
```

| Table | Rows | Used for |
|---|---|---|
| customers | 6 | filters, joins (2 never ordered, 1 has no email, 1 no city) |
| products | 8 | aggregates, CASE |
| orders | 8 | joins, statuses |
| order_items | 12 | 3-table joins |
| employees | 7 | self join, recursive CTE, windows |

## Lessons (in order)

| # | File | Topics |
|---|---|---|
| 1 | [select-filter](01-select-filter-modify.md) | SELECT, WHERE, ORDER BY, LIMIT, DISTINCT, NULL |
| 1b | [insert-update-delete](01b-insert-update-delete.md) | INSERT, UPDATE, DELETE, RETURNING |
| 2 | [aggregation](02-aggregation-case-functions.md) | COUNT/SUM/AVG/MIN/MAX, GROUP BY, HAVING, CASE, string & date functions |
| 3 | [joins](03-joins.md) | INNER, LEFT, RIGHT, FULL, CROSS, self |
| 4 | [subqueries & CTEs](04-subqueries-sets-ctes.md) | IN, EXISTS, UNION/INTERSECT/EXCEPT, CTE, recursive CTE |
| 5 | [window functions](05-window-functions.md) | RANK, running total, LAG |
| 6 | [transactions](06-transactions-commit-rollback.md) | BEGIN, COMMIT, ROLLBACK |

## SQL execution order (the thing that finally made errors make sense)

You *write* `SELECT` first, but the database *thinks* in this order:

```text
FROM / JOIN  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  ORDER BY  →  LIMIT
```

That's why you can't use a `SELECT` alias inside `WHERE`, and why `HAVING` can use aggregates but `WHERE` can't.

## Interview-style checklist

- [ ] Difference between `WHERE` and `HAVING`
- [ ] `INNER` vs `LEFT JOIN`
- [ ] `UNION` vs `UNION ALL`
- [ ] Why `= NULL` fails
- [ ] `RANK` vs `ROW_NUMBER`
- [ ] When to use a CTE

➡️ Next: [04 · Database Design](../04-database-design/)
