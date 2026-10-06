# 04 · Database Design

> Good queries can't rescue a bad design. This is how I go from a messy idea to clean tables.

```text
Requirements ──► Entities ──► Attributes ──► Relationships ──► Tables ──► Normalize ──► Schema
```

## 1. Requirements → entities

Take the sentence, underline the **nouns** (entities) and the **verbs** (relationships).

> "Students **enrol** in courses. Each course is **taught by** a teacher. Students get a **grade**."

| Noun → entity | Verb → relationship |
|---|---|
| Student, Course, Teacher | Student *enrols in* Course (N:M), Teacher *teaches* Course (1:N) |

## 2. ER diagram

```text
┌──────────┐ 1      N ┌─────────┐ N      M ┌──────────┐
│ Teacher  │──teaches─│ Course  │──enrols──│ Student  │
│----------│          │---------│          │----------│
│ id (PK)  │          │ id (PK) │          │ id (PK)  │
│ name     │          │ title   │          │ name     │
└──────────┘          │ teacher_id (FK)    │ email    │
                      └─────────┘          └──────────┘
```

- **Entity** = a thing (table). **Attribute** = a property (column).
- **Cardinality** = how many: 1:1, 1:N, N:M.
- N:M always becomes a **junction table** (`enrollments`).

## 3. Naming conventions I follow

| Rule | Example |
|---|---|
| lowercase `snake_case` | `order_items` |
| plural table names | `customers` |
| `id` as PK, `<table>_id` as FK | `orders.customer_id` |
| booleans start with `is_`/`has_` | `is_active` |
| timestamps end with `_at` | `created_at` |

## 4. Normalization: Bad → Problems → Better

```text
Bad Design ──► Identify Problems ──► Normalize ──► Better Design
```

### Bad design (one big table)

| order_id | customer | customer_phone | products | prices |
|---|---|---|---|---|
| 1 | Ayesha | 0300-111 | Laptop, Mouse | 950, 25 |
| 2 | Ayesha | 0300-111 | Desk | 220 |

### Problems (anomalies)

| Problem | Why it hurts |
|---|---|
| Repeating group (`products`, `prices` hold lists) | can't filter or sum properly |
| Duplicate data (Ayesha's phone twice) | |
| **Update anomaly** | change the phone → must change every row |
| **Insert anomaly** | can't add a customer who hasn't ordered yet |
| **Delete anomaly** | delete the only order → lose the customer |

### 1NF — atomic values, no repeating groups

Every cell holds **one** value; every row is unique.

| order_id | customer | customer_phone | product | price |
|---|---|---|---|---|
| 1 | Ayesha | 0300-111 | Laptop | 950 |
| 1 | Ayesha | 0300-111 | Mouse | 25 |
| 2 | Ayesha | 0300-111 | Desk | 220 |

Key is now `(order_id, product)`.

### 2NF — no partial dependency

Every non-key column must depend on the **whole** key. `customer` depends only on `order_id`, `price` only on `product`. Split:

```text
orders(order_id, customer, customer_phone)
products(product, price)
order_items(order_id, product)
```

### 3NF — no transitive dependency

Non-key columns must depend on **only the key**. `customer_phone` depends on `customer`, not on the order. Split again:

```text
customers(customer_id PK, name, phone)
orders(order_id PK, customer_id FK)
products(product_id PK, name, price)
order_items(order_id FK, product_id FK, quantity)   ← PK (order_id, product_id)
```

**Memory trick:** every column depends on *the key, the whole key, and nothing but the key.*

### Better design

```text
customers ──< orders ──< order_items >── products
```

That's exactly the [`shop`](../03-sql-postgresql/practice-db/schema.sql) database.

## 5. Denormalization

Deliberately adding duplicate data **for speed**.

| Normalized | Denormalized |
|---|---|
| no duplicates, safe updates | fewer joins, faster reads |
| more joins | risk of inconsistent copies |
| OLTP (apps) | OLAP, reports, caches |

```sql
-- storing a total on the order instead of summing items every time
ALTER TABLE orders ADD COLUMN total NUMERIC(10,2);
```

**Rule I follow:** normalise first, denormalise only when a measured query is too slow.

## 6. Common design mistakes

- ❌ Storing lists in one column (`'laptop,mouse'`)
- ❌ No primary key
- ❌ Using `FLOAT` for money
- ❌ Natural keys that change (email, phone) as PKs
- ❌ No foreign keys "because it's faster" (it isn't worth the broken data)
- ❌ One giant "god table"
- ❌ Vague column names (`data`, `value`, `info`)
- ❌ Skipping constraints and "validating in the app only"

## ✏️ Practice

1. Design a **library**: books, authors, members, loans. Draw the ER diagram, mark cardinalities.
2. Normalise this: `(student, course1, course2, course3, teacher_of_course1 ...)`.
3. Find one place in [`school.sql`](../02-relational-databases/school.sql) where I used a junction table.

➡️ Next: [05 · Transactions & Concurrency](../05-transactions-concurrency/)
