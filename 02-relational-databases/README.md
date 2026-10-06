# 02 · Relational Databases (PostgreSQL)

> From "what is a table" to a working PostgreSQL database with relationships, views, triggers and transactions.

Files here are **runnable**:

| File | Teaches |
|---|---|
| [`school.sql`](school.sql) | Students → Courses → Enrollments: schemas, constraints, all 3 relationship types, view, sequence, function, trigger |
| [`payments.sql`](payments.sql) | Users → Payments: CHECK rules and a transaction |
| [`../03-sql-postgresql/practice-db/`](../03-sql-postgresql/practice-db/) | Customers → Orders → Products |

## 1. Install & connect

```bash
# Ubuntu / Debian
sudo apt install postgresql postgresql-contrib
sudo service postgresql start

# macOS
brew install postgresql@16 && brew services start postgresql@16

# Windows: use the EnterpriseDB installer, or WSL + the Ubuntu commands.
# Docker (works everywhere):
docker run --name pg -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres:16
```

```bash
psql -U postgres                  # connect (add -h localhost if needed)
psql -U postgres -d school        # connect straight into a database
psql -U postgres -f school.sql    # run a file
```

### psql cheat sheet

| Command | Does |
|---|---|
| `\l` | list databases |
| `\c school` | connect to a database |
| `\dn` | list schemas |
| `\dt uni.*` | list tables in a schema |
| `\d students` | describe a table |
| `\dv` · `\df` | list views · functions |
| `\x` | toggle expanded output |
| `\timing` | show query time |
| `\i file.sql` | run a file |
| `\q` | quit |

> ⚠️ **Common mistake:** forgetting the `;`. If the prompt becomes `postgres-#` psql is waiting for more input.

## 2. Database, schema, table

```text
PostgreSQL server
 └── database  (school)
      └── schema  (uni)
           └── table  (students)
```

```sql
CREATE DATABASE school;
\c school
CREATE SCHEMA uni;
SET search_path TO uni, public;   -- look in uni first
```

*Analogy:* server = building, database = floor, schema = room, table = cabinet.

## 3. Data types I actually use

| Type | For |
|---|---|
| `INT`, `BIGINT`, `SERIAL` | whole numbers, auto ids |
| `NUMERIC(10,2)` | money (never `FLOAT`) |
| `TEXT` | any string |
| `BOOLEAN` | true/false |
| `DATE`, `TIMESTAMPTZ` | dates, timestamps with timezone |
| `JSONB` | flexible JSON inside Postgres |
| `UUID` | globally unique ids |

## 4. Constraints in action

```sql
age     INT CHECK (age >= 16),
email   TEXT UNIQUE NOT NULL,
credits INT NOT NULL DEFAULT 3,
```

Break a rule and PostgreSQL stops you:

```text
school=# INSERT INTO students(name,email,age) VALUES ('Kid','k@uni.edu',12);
ERROR:  new row for relation "students" violates check constraint "students_age_check"

school=# INSERT INTO enrollments VALUES (1,1,'B');
ERROR:  duplicate key value violates unique constraint "enrollments_pkey"
DETAIL:  Key (student_id, course_id)=(1, 1) already exists.
```

**Why:** the database becomes the last line of defence, even if the app has bugs.

## 5. Relationships

```text
ONE-TO-ONE            students ──1:1── student_profiles      (FK is also the PK)

ONE-TO-MANY           customers ──1:N── orders               (FK on the "many" side)

MANY-TO-MANY          students ──N:M── courses
                          students 1──N enrollments N──1 courses
                          (junction table holds both FKs)
```

`ON DELETE CASCADE` = delete the student → their enrollments disappear too.

✏️ **Try it:** what happens if you delete a course that has enrollments? (Hint: no cascade on that FK.)

## 6. Views

A **view** is a saved query you can `SELECT` from.

```sql
SELECT * FROM student_courses ORDER BY 1,2;
```
```text
    name     |       title       | grade
-------------+-------------------+-------
 Ayesha Khan | Algorithms        | B
 Ayesha Khan | Databases         | A
 Bilal Ahmed | Databases         | B
 Sara Malik  | Operating Systems | A
```

**Use when:** you repeat the same join, or want to hide columns from some users.

## 7. Sequences

```sql
SELECT nextval('receipt_no'), nextval('receipt_no');
```
```text
 nextval | nextval
---------+---------
    1000 |    1001
```

> ⚠️ Sequences never roll back. A failed insert still "uses up" a number — gaps in ids are normal.

## 8. Functions

```sql
SELECT name, ROUND(AVG(gpa_points(grade)),2) AS gpa
FROM student_courses GROUP BY name ORDER BY name;
```
```text
    name     | gpa
-------------+------
 Ayesha Khan | 3.50
 Bilal Ahmed | 3.00
 Sara Malik  | 4.00
```

## 9. Triggers

A trigger runs automatically when data changes. Here: log every grade change.

```sql
UPDATE enrollments SET grade='A' WHERE student_id=1 AND course_id=2;
SELECT student_id, course_id, old_grade, new_grade FROM grade_log;
```
```text
 student_id | course_id | old_grade | new_grade
------------+-----------+-----------+-----------
          1 |         2 | B         | A
```

**Use when:** audit logs, auto timestamps. **Avoid** hiding business logic in triggers — it surprises people.

## 10. Transactions

```sql
BEGIN;
UPDATE users SET balance = balance - 200 WHERE id = 1;
UPDATE users SET balance = balance + 200 WHERE id = 2;
COMMIT;
```

If something fails (say the balance would go negative) everything can be undone with `ROLLBACK`:

```text
pay=# UPDATE users SET balance = balance - 900 WHERE id=1;
ERROR:  new row for relation "users" violates check constraint "users_balance_check"
```

Full story in [05 · Transactions & Concurrency](../05-transactions-concurrency/).

## ✏️ Practice

1. Add a `teachers` table and make it one-to-many with `courses`.
2. Create a view `top_students` showing students with an average above 3.5.
3. Write a trigger that sets `updated_at = now()` on every update.

➡️ Next: [03 · SQL + PostgreSQL](../03-sql-postgresql/)
