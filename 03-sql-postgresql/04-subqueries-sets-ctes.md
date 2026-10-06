# 04 · Subqueries, set operations, CTEs

Queries inside queries, and ways to keep them readable.

> Setup: load [`practice-db`](practice-db/) first, then `psql -U postgres -d shop`.

---

### Subquery

**Problem:** Products priced above the average.

```sql
SELECT name, price FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;
```

```text
  name  | price  
--------+--------
 Laptop | 950.00
 Phone  | 600.00
(2 rows)
```

**Why it works:** The inner query runs first and returns one value.

---

### IN

**Problem:** Customers who ordered at least once.

```sql
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM orders) ORDER BY name;
```

```text
    name     
-------------
 Ayesha Khan
 Bilal Ahmed
 Hamza Ali
 Sara Malik
(4 rows)
```

**Why it works:** Checks membership in a list.

> ⚠️ **Common mistake:** `NOT IN` with a subquery that can return NULL gives zero rows. Prefer `NOT EXISTS`.

---

### EXISTS

**Problem:** Customers with **no** orders.

```sql
SELECT name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

```text
    name     
-------------
 Zainab Noor
 Usman Tariq
(2 rows)
```

**Why it works:** `EXISTS` only asks 'is there at least one row?' — fast and NULL-safe.

---

### UNION

**Problem:** All cities mentioned (customers) plus category names, as one list.

```sql
SELECT city AS label FROM customers WHERE city IS NOT NULL
UNION
SELECT category FROM products
ORDER BY label;
```

```text
    label    
-------------
 Accessories
 Electronics
 Furniture
 Islamabad
 Karachi
 Lahore
 Stationery
(7 rows)
```

**Why it works:** Stacks results and removes duplicates. `UNION ALL` keeps duplicates and is faster.

---

### INTERSECT

**Problem:** Customers who have a paid order AND a shipped order.

```sql
SELECT customer_id FROM orders WHERE status='paid'
INTERSECT
SELECT customer_id FROM orders WHERE status='shipped';
```

```text
 customer_id 
-------------
           1
(1 row)
```

**Why it works:** Rows that appear in both results.

---

### EXCEPT

**Problem:** Customers with a paid order but no shipped order.

```sql
SELECT customer_id FROM orders WHERE status='paid'
EXCEPT
SELECT customer_id FROM orders WHERE status='shipped'
ORDER BY 1;
```

```text
 customer_id 
-------------
           2
           4
(2 rows)
```

**Why it works:** In the first result but not the second.

---

### CTE (WITH)

**Problem:** Customers whose total spending is above the average customer total.

```sql
WITH totals AS (
  SELECT o.customer_id, SUM(oi.quantity*p.price) AS spent
  FROM orders o
  JOIN order_items oi ON oi.order_id=o.id
  JOIN products p ON p.id=oi.product_id
  WHERE o.status <> 'cancelled'
  GROUP BY o.customer_id
)
SELECT c.name, t.spent
FROM totals t JOIN customers c ON c.id=t.customer_id
WHERE t.spent > (SELECT AVG(spent) FROM totals)
ORDER BY t.spent DESC;
```

```text
    name     |  spent  
-------------+---------
 Hamza Ali   | 1200.00
 Ayesha Khan | 1104.00
(2 rows)
```

**Why it works:** A CTE is a named temporary result — a variable for a query. Much easier to read than nested subqueries.

---

### Recursive CTE

**Problem:** Print the whole company tree starting from the CEO, with depth.

```sql
WITH RECURSIVE team AS (
  SELECT id, name, 0 AS depth FROM employees WHERE name='Omar'
  UNION ALL
  SELECT e.id, e.name, t.depth+1
  FROM employees e JOIN team t ON e.manager_id = t.id
)
SELECT REPEAT('  ', depth) || name AS org_chart, depth FROM team;
```

```text
  org_chart  | depth 
-------------+-------
 Omar        |     0
   Hina      |     1
   Rizwan    |     1
     Fahad   |     2
     Mehwish |     2
     Nida    |     2
     Talha   |     2
(7 rows)
```

**Why it works:** Part 1 is the starting row. Part 2 keeps joining children to what we already found, until nothing new appears.

> ⚠️ **Common mistake:** No stopping condition → infinite loop on cyclic data.

✏️ **Try it:** Start from 'Rizwan' instead.

---

