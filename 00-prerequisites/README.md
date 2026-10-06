# 00 · Prerequisites

> The tiny vocabulary I needed before anything else made sense. Each idea is a few lines — skim, then move on.

```text
Data ──► stored in a Database ──► managed by a DBMS ──► used by a Client
```

## Data vs Information

**Data** is raw facts. **Information** is data that means something.

| Data | Information |
|---|---|
| `Ayesha, 21, 3.8` | "Ayesha is 21 and has a 3.8 GPA" |

*Analogy:* flour is data, bread is information.

## Database, DBMS, Server, Client

```text
 ┌────────┐   query    ┌─────────────────┐        ┌──────────┐
 │ Client │ ─────────► │ Database Server │ ─────► │ Database │
 │ (psql, │ ◄───────── │ (PostgreSQL     │ ◄───── │  (files  │
 │  app)  │   result   │  = the DBMS)    │        │ on disk) │
 └────────┘            └─────────────────┘        └──────────┘
```

- **Database** – organised collection of data.
- **DBMS** – software that stores, protects and queries it (PostgreSQL, MongoDB, Redis).
- **Database server** – the running DBMS process, waiting for requests.
- **Client** – anything that talks to the server: `psql`, a Python script, a web app.

*Analogy:* database = library books, DBMS = the librarian, client = you at the desk.

## Tables, Rows, Columns, Records

```text
students                       ← table
┌────┬─────────────┬─────┐
│ id │ name        │ age │     ← columns (attributes)
├────┼─────────────┼─────┤
│  1 │ Ayesha Khan │  21 │     ← row = record
│  2 │ Bilal Ahmed │  22 │
└────┴─────────────┴─────┘
```

A **record** and a **row** are the same thing in practice.

## Primary key & Foreign key

- **Primary key (PK):** column that uniquely identifies each row. Never repeats, never NULL.
- **Foreign key (FK):** column that points to another table's primary key.

```text
students                 enrollments
┌────┬──────────┐        ┌────┬────────────┬───────────┐
│ id │ name     │        │ id │ student_id │ course_id │
│ 1  │ Ayesha   │◄───────│ 10 │     1      │    5      │
└────┴──────────┘        └────┴────────────┴───────────┘
  PK                           FK → students.id
```

> ⚠️ **Common mistake:** using something that can change (like a name or email) as the primary key.

## Relationships

| Type | Example |
|---|---|
| One-to-one | user ↔ profile |
| One-to-many | customer → many orders |
| Many-to-many | students ↔ courses (needs a middle table) |

## CRUD

Almost every app is these four:

| Letter | Meaning | SQL |
|---|---|---|
| **C** | Create | `INSERT` |
| **R** | Read | `SELECT` |
| **U** | Update | `UPDATE` |
| **D** | Delete | `DELETE` |

## Schema

The **blueprint**: which tables exist, their columns, types and rules. *Analogy:* the floor plan of a house, not the furniture.

## Structured vs Unstructured data

| Structured | Semi-structured | Unstructured |
|---|---|---|
| fits rows & columns | JSON, has loose shape | text, images, audio |
| PostgreSQL | MongoDB | files, vector DBs (as embeddings) |

## ✏️ Practice

1. Draw a table for `books` with 4 columns and 3 rows.
2. Which column is the primary key? Why?
3. Add an `authors` table. How would `books` point to it?

➡️ Next: [01 · Database Fundamentals](../01-database-fundamentals/)
