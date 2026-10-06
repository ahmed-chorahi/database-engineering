# Project 2 — E-Commerce Database

**Databases:** PostgreSQL · **Files:** [`schema.sql`](schema.sql) · [`queries.sql`](queries.sql) · [`indexing.sql`](indexing.sql)

## Problem
An online shop needs to store customers, products, orders and payments — and stay fast with 100,000 orders.

## Requirements
- Orders have many items; a product can be in many orders.
- Remember the **price at purchase time** (products get repriced later).
- Payments linked to orders; stock can never go negative.
- Order history for one customer must be instant.

## Choose database
**PostgreSQL** — money + inventory = ACID and constraints.

## Design (normalised)
```text
customers ──< orders ──< order_items >── products >── categories
                │
                └──< payments

order_items.unit_price  ← deliberate copy: history must not change when price changes
```

## Implementation
```bash
psql -U postgres -f schema.sql      # creates tables AND generates 100k orders / 300k items
```
`generate_series()` + `random()` builds realistic volume without any CSV.

## Queries (real run)
```sql
-- revenue per category
SELECT c.name, SUM(oi.quantity*oi.unit_price)::numeric(12,0) AS revenue
FROM order_items oi JOIN products p ON p.id=oi.product_id JOIN categories c ON c.id=p.category_id
JOIN orders o ON o.id=oi.order_id WHERE o.status <> 'cancelled' GROUP BY c.name ORDER BY revenue DESC;
```
```text
    name    | revenue
------------+----------
 Category 3 | 40065100
 Category 2 | 37227109
 ...
```
(Data is random — your numbers will differ.)

## Testing
- `INSERT INTO order_items ... quantity = 0` → fails `CHECK`.
- Delete an order → its items disappear (`ON DELETE CASCADE`), payments block it (no cascade — on purpose).

## Performance — the slow query
Order history of one customer, run `indexing.sql`:

| | Plan | Time |
|---|---|---|
| Before | `Seq Scan on orders` | **6.3 ms** |
| After `CREATE INDEX ... (customer_id, created_at DESC)` | `Bitmap Index Scan` | **0.11 ms** |

The composite index covers both the filter *and* the sort. Bonus lesson: **PostgreSQL does not auto-index foreign keys** — `payments.order_id` needed its own index (`idx_payments_order`).

## What I learned
- Store history values (`unit_price`) even though it "duplicates" data.
- Index foreign keys and the columns you filter + sort by.
- `EXPLAIN ANALYZE` before and after — never guess.
