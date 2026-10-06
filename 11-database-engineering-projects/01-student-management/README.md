# Project 1 — Student Management System

**Databases:** PostgreSQL · **Files:** [`schema.sql`](schema.sql) · [`queries.sql`](queries.sql)

## Problem
A university tracks students, departments, courses and marks in spreadsheets. Data is duplicated and inconsistent.

## Requirements
- A student belongs to one department.
- A student can take many courses; a course has many students; each enrollment has marks (0–100, may be empty).
- Emails and course codes must be unique.
- Reports: averages, toppers, students with no courses.

## Choose database
**PostgreSQL** — structured, relational, rules matter (no marks of 150).

## Design
```text
departments ──< students ──< enrollments >── courses >── departments
                (N:M junction: PK = student_id + course_id)
```
Normalised to 3NF; `CHECK`, `UNIQUE`, `FOREIGN KEY` enforce the rules.

## Implementation
```bash
psql -U postgres -f schema.sql
```

## Queries (real run)
```sql
-- Average marks per course
SELECT c.code, c.title, ROUND(AVG(e.marks),1) AS avg_marks, COUNT(e.marks) AS graded
FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id GROUP BY c.id ORDER BY c.code;
```
```text
 code  |   title    | avg_marks | graded
-------+------------+-----------+--------
 CS201 | Databases  |      81.5 |      2
 CS202 | Algorithms |      84.0 |      1
 MA101 | Calculus   |      76.5 |      2
```
```sql
-- Students not enrolled anywhere
SELECT name FROM students s WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id = s.id);
```
```text
    name
-------------
 Usman Tariq
```
See `queries.sql` for CRUD, joins, a window-function "topper per course", and a credit-weighted average.

## Testing
Try to break the rules — each should fail:
```sql
INSERT INTO enrollments VALUES (4, 2, 150);          -- CHECK violation (marks > 100)
INSERT INTO students (name,email,dept_id) VALUES ('X','ayesha@uni.edu',1);   -- UNIQUE violation
DELETE FROM courses WHERE id = 1;                     -- FK violation (has enrollments)
```

## Performance
Tiny data, so nothing to optimise yet. Note `AVG` ignores NULL marks (Hamza's) — that's correct, not a bug.

## What I learned
- Constraints catch bad data before it exists.
- `LEFT JOIN` + `COUNT(col)` correctly counts "zero".
- A junction table is just two foreign keys and a primary key.
