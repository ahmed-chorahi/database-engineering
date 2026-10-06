# MongoDB

## Setup

```bash
docker run --name mongo -p 27017:27017 -d mongo:7
docker exec -it mongo mongosh          # the Mongo shell
```
Python: `pip install pymongo` → see [`mongo_demo.py`](mongo_demo.py).

## Core vocabulary (mapped to SQL)

| PostgreSQL | MongoDB |
|---|---|
| database | database |
| table | **collection** |
| row | **document** |
| column | field |
| JOIN | embed / `$lookup` |

A **document** is JSON-like, stored as **BSON** (binary JSON — adds types like `Date`, `ObjectId`, `Int64`, and is faster to scan).

```json
{
  "_id": "ObjectId('65f...')",
  "name": "Ayesha Khan",
  "age": 21,
  "skills": ["sql", "python"],
  "address": { "city": "Islamabad", "zip": "44000" }
}
```
Every document gets a unique `_id` (the primary key).

## CRUD

```js
use school

// Create
db.students.insertOne({ name: "Ayesha", age: 21, skills: ["sql", "python"] })
db.students.insertMany([
  { name: "Bilal", age: 22, skills: ["java"] },
  { name: "Sara",  age: 20, skills: ["python", "ml"], city: "Karachi" }
])

// Read
db.students.find()                          // everything
db.students.find({ age: { $gt: 20 } })      // age > 20
db.students.find({ skills: "python" })      // array contains
db.students.find({}, { name: 1, _id: 0 })   // projection (pick fields)
db.students.find().sort({ age: -1 }).limit(2)

// Update
db.students.updateOne({ name: "Bilal" }, { $set: { age: 23 } })
db.students.updateOne({ name: "Bilal" }, { $push: { skills: "sql" } })

// Delete
db.students.deleteOne({ name: "Sara" })
```

Expected for `db.students.find({ skills: "python" }, { name: 1, _id: 0 })`:

```text
[ { name: 'Ayesha' }, { name: 'Sara' } ]
```

> ⚠️ **Common mistake:** `updateOne({...}, { age: 23 })` without `$set` — it errors (or in older APIs, replaces the whole document).

## Query operators

| Operator | Meaning | SQL cousin |
|---|---|---|
| `$eq` `$ne` | equal / not equal | `=` `<>` |
| `$gt` `$gte` `$lt` `$lte` | comparisons | `>` `>=` `<` `<=` |
| `$in` `$nin` | in a list | `IN` |
| `$and` `$or` `$not` | logic | `AND` `OR` `NOT` |
| `$exists` | field present? | `IS NOT NULL` |
| `$regex` | pattern | `LIKE` |

```js
db.students.find({ $or: [{ age: { $lt: 21 } }, { city: { $exists: true } }] })
```

## Embedded documents vs references

```text
EMBED  (one read, data lives together)       REFERENCE  (like a foreign key)
{ _id: 1,                                    orders:  { _id: 10, customer_id: 1, ... }
  name: "Ayesha",                            customers: { _id: 1, name: "Ayesha" }
  orders: [ {item:"Laptop"}, {item:"Pen"} ]
}
```

| Embed when | Reference when |
|---|---|
| data is read together | child data grows without limit |
| "owned" by the parent (comments on a post) | many parents share it (a product) |
| 1:few | 1:many / many:many |

> ⚠️ Documents max out at **16 MB** — never embed an unbounded array.

## Schema design — "design for your queries"

In SQL I model the **data** then write queries. In MongoDB I model for the **queries** I'll run most:

1. List the queries.
2. Embed what is read together.
3. Reference what grows or is shared.
4. Accept some duplication (denormalisation) for speed.

## Indexes

Same idea as [06](../06-indexing-query-performance/):

```js
db.students.createIndex({ age: 1 })
db.students.createIndex({ city: 1, age: -1 })          // compound
db.students.find({ age: 21 }).explain("executionStats")
```
Look for `IXSCAN` (index) vs `COLLSCAN` (full collection scan = Seq Scan).

## Aggregation pipeline

Data flows through stages, like a Unix pipe — each stage transforms the output of the last.

```text
documents ─► $match ─► $group ─► $sort ─► $limit ─► result
```

```js
// average age per city, only cities with 2+ students
db.students.aggregate([
  { $match: { age: { $gte: 18 } } },
  { $group: { _id: "$city", avg_age: { $avg: "$age" }, n: { $sum: 1 } } },
  { $match: { n: { $gte: 2 } } },
  { $sort: { avg_age: -1 } }
])
```

SQL equivalent:

```sql
SELECT city, AVG(age), COUNT(*) FROM students
WHERE age >= 18 GROUP BY city HAVING COUNT(*) >= 2 ORDER BY AVG(age) DESC;
```

`$lookup` is MongoDB's (limited) JOIN:

```js
db.orders.aggregate([{ $lookup: { from: "customers", localField: "customer_id", foreignField: "_id", as: "customer" } }])
```

## MongoDB vs PostgreSQL

| Choose MongoDB when | Choose PostgreSQL when |
|---|---|
| fields differ between records (product catalogs, CMS, logs) | data is relational with rules (finance, inventory) |
| nested data is read as a whole | you need many joins & ad-hoc reporting |
| schema changes constantly early on | you want the DB to enforce integrity |

## ✏️ Practice

1. Insert 5 products with different fields. Find those under 100.
2. Model a blog: embed comments or reference them? Defend your choice.
3. Write the pipeline: top 3 categories by number of products.
