# 02 · Aggregates, GROUP BY, CASE, string and date functions

Collapse many rows into answers.

> Setup: load [`practice-db`](practice-db/) first, then `psql -U postgres -d shop`.

---

### COUNT / SUM / AVG / MIN / MAX

**Problem:** Price statistics for all products.

```sql
SELECT COUNT(*) AS items, MIN(price) AS cheapest, MAX(price) AS priciest,
       ROUND(AVG(price),2) AS avg_price, SUM(price) AS total
FROM products;
```

```text
 items | cheapest | priciest | avg_price |  total  
-------+----------+----------+-----------+---------
     8 |     3.50 |   950.00 |    254.19 | 2033.50
(1 row)
```

**Why it works:** Aggregates squash all rows into one.

> ⚠️ **Common mistake:** `COUNT(col)` skips NULLs, `COUNT(*)` does not. Compare `COUNT(email)` vs `COUNT(*)` on customers.

✏️ **Try it:** Count customers per city.

---

### GROUP BY

**Problem:** Products and average price per category.

```sql
SELECT category, COUNT(*) AS products, ROUND(AVG(price),2) AS avg_price
FROM products GROUP BY category ORDER BY avg_price DESC;
```

```text
  category   | products | avg_price 
-------------+----------+-----------
 Electronics |        3 |    543.33
 Furniture   |        2 |    175.00
 Accessories |        1 |     45.00
 Stationery  |        2 |      4.25
(4 rows)
```

**Why it works:** One output row per group.

> ⚠️ **Common mistake:** Selecting a column that is not in `GROUP BY` and not aggregated — PostgreSQL will error.

---

### HAVING

**Problem:** Categories with more than 2 products.

```sql
SELECT category, COUNT(*) FROM products GROUP BY category HAVING COUNT(*) > 2;
```

```text
  category   | count 
-------------+-------
 Electronics |     3
(1 row)
```

**Why it works:** `WHERE` filters rows *before* grouping, `HAVING` filters groups *after*.

> ⚠️ **Common mistake:** Using an aggregate inside `WHERE`.

---

### CASE

**Problem:** Label products as cheap / mid / premium.

```sql
SELECT name, price,
  CASE WHEN price < 50 THEN 'cheap'
       WHEN price < 300 THEN 'mid'
       ELSE 'premium' END AS tier
FROM products ORDER BY price;
```

```text
    name    | price  |  tier   
------------+--------+---------
 Notebook   |   3.50 | cheap
 Pen Pack   |   5.00 | cheap
 Backpack   |  45.00 | cheap
 Headphones |  80.00 | mid
 Chair      | 130.00 | mid
 Desk       | 220.00 | mid
 Phone      | 600.00 | premium
 Laptop     | 950.00 | premium
(8 rows)
```

**Why it works:** `CASE` is SQL's if/else. First matching branch wins.

---

### String functions

**Problem:** Clean up names and emails.

```sql
SELECT UPPER(name) AS upper_name, LENGTH(name) AS len,
       SPLIT_PART(email,'@',1) AS username,
       name || ' from ' || COALESCE(city,'?') AS label
FROM customers WHERE email IS NOT NULL;
```

```text
 upper_name  | len | username |           label            
-------------+-----+----------+----------------------------
 AYESHA KHAN |  11 | ayesha   | Ayesha Khan from Islamabad
 BILAL AHMED |  11 | bilal    | Bilal Ahmed from Lahore
 SARA MALIK  |  10 | sara     | Sara Malik from Karachi
 HAMZA ALI   |   9 | hamza    | Hamza Ali from Lahore
 USMAN TARIQ |  11 | usman    | Usman Tariq from ?
(5 rows)
```

**Why it works:** `||` concatenates. Other handy ones: `LOWER`, `TRIM`, `SUBSTRING`, `REPLACE`.

---

### Date/time functions

**Problem:** Show the earliest customers with their join month and year.

```sql
SELECT name, joined_on,
       TO_CHAR(joined_on,'Mon YYYY') AS month,
       DATE_TRUNC('month', joined_on)::date AS month_start,
       EXTRACT(YEAR FROM joined_on) AS yr
FROM customers ORDER BY joined_on LIMIT 3;
```

```text
    name     | joined_on  |  month   | month_start |  yr  
-------------+------------+----------+-------------+------
 Ayesha Khan | 2024-01-15 | Jan 2024 | 2024-01-01  | 2024
 Bilal Ahmed | 2024-03-02 | Mar 2024 | 2024-03-01  | 2024
 Sara Malik  | 2024-03-20 | Mar 2024 | 2024-03-01  | 2024
(3 rows)
```

**Why it works:** `DATE_TRUNC` rounds down to a unit, `EXTRACT` pulls a part, `TO_CHAR` formats. `CURRENT_DATE - joined_on` gives days.

---

