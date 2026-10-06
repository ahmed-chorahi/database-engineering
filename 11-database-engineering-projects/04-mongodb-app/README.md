# Project 4 — MongoDB Application (Blog)

**Databases:** MongoDB · **File:** [`app.js`](app.js) → `mongosh app.js`

## Problem
A blog stores posts with tags and comments. Posts have different shapes over time (polls, images, videos...).

## Requirements
- Show a post with its comments in **one read**.
- Find posts by tag; list an author's latest posts.
- Stats: likes per author, most-used tags.

## Choose database
**MongoDB** — a post is a self-contained document; comments belong to one post; schema will evolve.

## Design — embed vs reference
```text
users   { _id, name, joined }                           ← referenced (shared, small)
posts   { title, author_id → users._id,                 ← reference to author
          tags: [..], likes,
          comments: [ {by, text, at}, ... ] }           ← embedded (read together, bounded)
```
Rule used: *embed what is read together and owned by the parent; reference what is shared.*

## Implementation
```bash
docker run --name mongo -p 27017:27017 -d mongo:7
mongosh app.js
```

## Queries — **(expected output, worked out from the data)**
```js
db.posts.aggregate([
  { $group: { _id: "$author_id", posts: { $sum: 1 }, total_likes: { $sum: "$likes" } } },
  { $lookup: { from: "users", localField: "_id", foreignField: "_id", as: "author" } },
  { $unwind: "$author" },
  { $project: { _id: 0, author: "$author.name", posts: 1, total_likes: 1 } },
  { $sort: { total_likes: -1 } }
])
```
```text
{ posts: 2, total_likes: 33, author: 'Ayesha' }
{ posts: 1, total_likes: 31, author: 'Bilal' }     ← 30 likes + 1 from the $inc update
```
Tag counts via `$unwind` + `$group`: `databases` appears twice, every other tag once.

## Testing
- Insert a post with a brand-new field (`poll: {...}`) — no migration needed.
- Insert a post without `tags` — `$unwind` skips it silently.

## Performance
`createIndex({ tags: 1 })` and `({ author_id: 1, created: -1 })`; check `explain("executionStats")` for `IXSCAN` instead of `COLLSCAN`.

## What I learned
- Design collections around queries, not around entities.
- `$lookup` works but if I need it everywhere, that's a sign I want PostgreSQL.
- Unbounded arrays (millions of comments) must be referenced, not embedded.
