# 05 · Window functions

Like `GROUP BY`, but **keeps every row**. The `OVER (...)` clause defines the window.

> Setup: load [`practice-db`](practice-db/) first, then `psql -U postgres -d shop`.

---

### ROW_NUMBER / RANK

**Problem:** Rank employees by salary inside each department.

```sql
SELECT dept, name, salary,
  RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank_in_dept
FROM employees ORDER BY dept, rank_in_dept;
```

```text
    dept     |  name   | salary  | rank_in_dept 
-------------+---------+---------+--------------
 Engineering | Hina    | 6000.00 |            1
 Engineering | Mehwish | 4800.00 |            2
 Engineering | Fahad   | 4500.00 |            3
 Management  | Omar    | 9000.00 |            1
 Sales       | Rizwan  | 4000.00 |            1
 Sales       | Talha   | 3600.00 |            2
 Sales       | Nida    | 3500.00 |            3
(7 rows)
```

**Why it works:** `PARTITION BY` = the groups, `ORDER BY` = the order inside each group.

> ⚠️ **Common mistake:** Trying to filter on a window function in `WHERE`. Wrap it in a CTE and filter outside.

---

### Aggregate as window

**Problem:** Each employee's salary next to their department average.

```sql
SELECT name, dept, salary,
  ROUND(AVG(salary) OVER (PARTITION BY dept),0) AS dept_avg,
  salary - ROUND(AVG(salary) OVER (PARTITION BY dept),0) AS diff
FROM employees ORDER BY dept, salary DESC;
```

```text
  name   |    dept     | salary  | dept_avg |  diff   
---------+-------------+---------+----------+---------
 Hina    | Engineering | 6000.00 |     5100 |  900.00
 Mehwish | Engineering | 4800.00 |     5100 | -300.00
 Fahad   | Engineering | 4500.00 |     5100 | -600.00
 Omar    | Management  | 9000.00 |     9000 |    0.00
 Rizwan  | Sales       | 4000.00 |     3700 |  300.00
 Talha   | Sales       | 3600.00 |     3700 | -100.00
 Nida    | Sales       | 3500.00 |     3700 | -200.00
(7 rows)
```

**Why it works:** No collapsing — every employee row survives.

---

### Running total

**Problem:** Cumulative spending of Ayesha's orders over time.

```sql
SELECT o.order_date, o.id,
  SUM(oi.quantity*p.price) AS order_total,
  SUM(SUM(oi.quantity*p.price)) OVER (ORDER BY o.order_date) AS running_total
FROM orders o
JOIN order_items oi ON oi.order_id=o.id
JOIN products p ON p.id=oi.product_id
WHERE o.customer_id = 1
GROUP BY o.id, o.order_date ORDER BY o.order_date;
```

```text
 order_date | id | order_total | running_total 
------------+----+-------------+---------------
 2024-08-01 |  1 |     1030.00 |       1030.00
 2024-08-15 |  2 |       60.00 |       1090.00
 2024-09-12 |  8 |       14.00 |       1104.00
(3 rows)
```

**Why it works:** `SUM(...) OVER (ORDER BY ...)` adds up everything from the first row to the current one.

---

### LAG

**Problem:** Days between each order and the customer's previous order.

```sql
SELECT customer_id, order_date,
  order_date - LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS days_since_prev
FROM orders WHERE customer_id IN (1,2,4) ORDER BY customer_id, order_date;
```

```text
 customer_id | order_date | days_since_prev 
-------------+------------+-----------------
           1 | 2024-08-01 |                
           1 | 2024-08-15 |              14
           1 | 2024-09-12 |              28
           2 | 2024-08-03 |                
           2 | 2024-09-01 |              29
           4 | 2024-09-05 |                
           4 | 2024-09-10 |               5
(7 rows)
```

**Why it works:** `LAG` looks at the previous row, `LEAD` at the next.

---

