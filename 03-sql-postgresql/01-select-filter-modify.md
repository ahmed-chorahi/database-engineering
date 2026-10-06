# 01 · SELECT, filtering and changing data

Everything starts with reading rows. Think of `SELECT` as asking the table a question.

> Setup: load [`practice-db`](practice-db/) first, then `psql -U postgres -d shop`.

---

### SELECT

**Problem:** Show every customer.

```sql
SELECT * FROM customers;
```

```text
 id |    name     |      email      |   city    | joined_on  
----+-------------+-----------------+-----------+------------
  1 | Ayesha Khan | ayesha@mail.com | Islamabad | 2024-01-15
  2 | Bilal Ahmed | bilal@mail.com  | Lahore    | 2024-03-02
  3 | Sara Malik  | sara@mail.com   | Karachi   | 2024-03-20
  4 | Hamza Ali   | hamza@mail.com  | Lahore    | 2024-05-11
  5 | Zainab Noor |                 | Islamabad | 2024-06-01
  6 | Usman Tariq | usman@mail.com  |           | 2024-07-09
(6 rows)
```

**Why it works:** `*` means all columns. Fine for exploring, avoid it in real code.

> ⚠️ **Common mistake:** Using `SELECT *` on big tables — it pulls columns you don't need.

✏️ **Try it:** Select only `name` and `city`.

---

### WHERE

**Problem:** Customers who live in Lahore.

```sql
SELECT name, city FROM customers WHERE city = 'Lahore';
```

```text
    name     |  city  
-------------+--------
 Bilal Ahmed | Lahore
 Hamza Ali   | Lahore
(2 rows)
```

**Why it works:** `WHERE` keeps only the rows where the condition is true.

> ⚠️ **Common mistake:** Using double quotes for text. In PostgreSQL `'text'` is a value, `"name"` is an identifier.

✏️ **Try it:** Find products costing more than 100.

---

### AND / OR / BETWEEN / IN / LIKE

**Problem:** Electronics priced between 50 and 700, name containing 'phone'.

```sql
SELECT name, price FROM products
WHERE category = 'Electronics' AND price BETWEEN 50 AND 700 AND name ILIKE '%phone%';
```

```text
    name    | price  
------------+--------
 Phone      | 600.00
 Headphones |  80.00
(2 rows)
```

**Why it works:** `ILIKE` is PostgreSQL's case-insensitive `LIKE`. `%` matches any characters.

✏️ **Try it:** List products in Furniture OR Stationery using `IN`.

---

### ORDER BY + LIMIT

**Problem:** The 3 most expensive products.

```sql
SELECT name, price FROM products ORDER BY price DESC LIMIT 3;
```

```text
  name  | price  
--------+--------
 Laptop | 950.00
 Phone  | 600.00
 Desk   | 220.00
(3 rows)
```

**Why it works:** Sort first, then cut. Without `ORDER BY`, `LIMIT` gives you arbitrary rows.

> ⚠️ **Common mistake:** Expecting a stable order without `ORDER BY`. Tables have no guaranteed order.

---

### DISTINCT

**Problem:** Which cities do customers come from?

```sql
SELECT DISTINCT city FROM customers ORDER BY city;
```

```text
   city    
-----------
 Islamabad
 Karachi
 Lahore
 
(4 rows)
```

**Why it works:** Removes duplicate rows from the result. Note the NULL city is still shown (NULLs sort last).

---

### NULL

**Problem:** Customers with no email.

```sql
SELECT name FROM customers WHERE email IS NULL;
```

```text
    name     
-------------
 Zainab Noor
(1 row)
```

**Why it works:** NULL means *unknown*, so `email = NULL` is never true. Use `IS NULL` / `IS NOT NULL`.

> ⚠️ **Common mistake:** Writing `= NULL`. It silently returns zero rows.

✏️ **Try it:** Use `COALESCE(city, 'Unknown')` to replace NULL cities.

---

### COALESCE

**Problem:** Show a friendly city even when it is NULL.

```sql
SELECT name, COALESCE(city,'Unknown') AS city FROM customers;
```

```text
    name     |   city    
-------------+-----------
 Ayesha Khan | Islamabad
 Bilal Ahmed | Lahore
 Sara Malik  | Karachi
 Hamza Ali   | Lahore
 Zainab Noor | Islamabad
 Usman Tariq | Unknown
(6 rows)
```

**Why it works:** `COALESCE` returns the first non-NULL argument.

---

