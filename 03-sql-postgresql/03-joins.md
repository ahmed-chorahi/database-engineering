# 03 · JOINs

Data is split across tables on purpose (see 04-database-design). Joins glue it back.

```text
customers.id  ──┐
                 ├── orders.customer_id
 orders.id    ──┘
```

> Setup: load [`practice-db`](practice-db/) first, then `psql -U postgres -d shop`.

---

### INNER JOIN

**Problem:** Order id, customer name and status for every order.

```sql
SELECT o.id, c.name, o.status
FROM orders o
JOIN customers c ON c.id = o.customer_id
ORDER BY o.id;
```

```text
 id |    name     |  status   
----+-------------+-----------
  1 | Ayesha Khan | paid
  2 | Ayesha Khan | shipped
  3 | Bilal Ahmed | paid
  4 | Bilal Ahmed | cancelled
  5 | Sara Malik  | shipped
  6 | Hamza Ali   | pending
  7 | Hamza Ali   | paid
  8 | Ayesha Khan | paid
(8 rows)
```

**Why it works:** Keeps only rows that match on both sides.

> ⚠️ **Common mistake:** Forgetting the `ON` condition → every row paired with every row.

---

### LEFT JOIN

**Problem:** Every customer, even those who never ordered.

```sql
SELECT c.name, COUNT(o.id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.name ORDER BY orders DESC, c.name;
```

```text
    name     | orders 
-------------+--------
 Ayesha Khan |      3
 Bilal Ahmed |      2
 Hamza Ali   |      2
 Sara Malik  |      1
 Usman Tariq |      0
 Zainab Noor |      0
(6 rows)
```

**Why it works:** Keeps all left rows; missing matches become NULL (so the count is 0).

> ⚠️ **Common mistake:** Putting a filter on the right table in `WHERE` — it turns the LEFT JOIN back into an INNER JOIN.

✏️ **Try it:** Find customers with no orders using `WHERE o.id IS NULL`.

---

### RIGHT JOIN

**Problem:** Same idea, mirrored: every product, even if never sold.

```sql
SELECT p.name, oi.order_id
FROM order_items oi
RIGHT JOIN products p ON p.id = oi.product_id
WHERE oi.order_id IS NULL;
```

```text
 name | order_id 
------+----------
(0 rows)
```

**Why it works:** Rarely needed — just swap table order and use LEFT JOIN. Here: no product is unsold, so zero rows.

---

### FULL JOIN

**Problem:** All customers and all orders, matched where possible.

```sql
SELECT c.name, o.id AS order_id
FROM customers c FULL JOIN orders o ON o.customer_id = c.id
WHERE c.id IS NULL OR o.id IS NULL;
```

```text
    name     | order_id 
-------------+----------
 Zainab Noor |         
 Usman Tariq |         
(2 rows)
```

**Why it works:** Keeps unmatched rows from both sides. Useful for finding mismatches between two lists.

---

### CROSS JOIN

**Problem:** Every customer × every category (for a promo grid).

```sql
SELECT c.name, k.category
FROM (SELECT name FROM customers LIMIT 2) c
CROSS JOIN (SELECT DISTINCT category FROM products ORDER BY 1 LIMIT 2) k;
```

```text
    name     |  category   
-------------+-------------
 Ayesha Khan | Accessories
 Ayesha Khan | Electronics
 Bilal Ahmed | Accessories
 Bilal Ahmed | Electronics
(4 rows)
```

**Why it works:** All combinations. 2 × 2 = 4 rows. Be careful with big tables.

---

### Self JOIN

**Problem:** Each employee with their manager's name.

```sql
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id
ORDER BY e.id;
```

```text
 employee | manager 
----------+---------
 Omar     | 
 Hina     | Omar
 Fahad    | Hina
 Mehwish  | Hina
 Rizwan   | Omar
 Nida     | Rizwan
 Talha    | Rizwan
(7 rows)
```

**Why it works:** The same table used twice under different aliases.

---

### Joining three tables

**Problem:** Revenue per order.

```sql
SELECT o.id, c.name, SUM(oi.quantity * p.price) AS total
FROM orders o
JOIN customers c    ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id
GROUP BY o.id, c.name ORDER BY o.id;
```

```text
 id |    name     |  total  
----+-------------+---------
  1 | Ayesha Khan | 1030.00
  2 | Ayesha Khan |   60.00
  3 | Bilal Ahmed |  600.00
  4 | Bilal Ahmed |  220.00
  5 | Sara Malik  |  305.00
  6 | Hamza Ali   |  160.00
  7 | Hamza Ali   | 1040.00
  8 | Ayesha Khan |   14.00
(8 rows)
```

**Why it works:** Chain joins one relationship at a time.

✏️ **Try it:** Which customer spent the most (ignore cancelled orders)?

---

