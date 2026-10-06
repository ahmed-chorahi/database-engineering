// mongosh blog_app app.js     (or paste into mongosh)
use("blog_app");
db.posts.drop(); db.users.drop();

db.users.insertMany([
  { _id: "u1", name: "Ayesha", joined: new Date("2024-01-10") },
  { _id: "u2", name: "Bilal",  joined: new Date("2024-02-20") }
]);

// Posts EMBED comments (read together) and REFERENCE the author (users are shared)
db.posts.insertMany([
  { title: "Why I like SQL",   author_id: "u1", tags: ["sql","databases"], likes: 12,
    comments: [{ by: "u2", text: "Same!", at: new Date() }], created: new Date("2024-03-01") },
  { title: "Redis in 10 minutes", author_id: "u2", tags: ["redis","cache"], likes: 30,
    comments: [], created: new Date("2024-03-05") },
  { title: "MongoDB schema design", author_id: "u1", tags: ["mongodb","databases"], likes: 21,
    comments: [{ by: "u2", text: "Embed or reference?", at: new Date() }, { by: "u1", text: "Depends!", at: new Date() }],
    created: new Date("2024-03-09") }
]);

// ---- Read
print("posts tagged databases:");
db.posts.find({ tags: "databases" }, { title: 1, _id: 0 }).forEach(printjson);

// ---- Update
db.posts.updateOne({ title: "Redis in 10 minutes" }, { $inc: { likes: 1 }, $push: { comments: { by: "u1", text: "Nice", at: new Date() } } });

// ---- Aggregation: total likes and post count per author, with author name via $lookup
db.posts.aggregate([
  { $group: { _id: "$author_id", posts: { $sum: 1 }, total_likes: { $sum: "$likes" } } },
  { $lookup: { from: "users", localField: "_id", foreignField: "_id", as: "author" } },
  { $unwind: "$author" },
  { $project: { _id: 0, author: "$author.name", posts: 1, total_likes: 1 } },
  { $sort: { total_likes: -1 } }
]).forEach(printjson);

// ---- Aggregation: most used tags ($unwind explodes the array)
db.posts.aggregate([{ $unwind: "$tags" }, { $group: { _id: "$tags", n: { $sum: 1 } } }, { $sort: { n: -1 } }, { $limit: 3 }]).forEach(printjson);

// ---- Indexing
db.posts.createIndex({ tags: 1 });
db.posts.createIndex({ author_id: 1, created: -1 });
printjson(db.posts.find({ author_id: "u1" }).sort({ created: -1 }).explain("executionStats").executionStats.executionStages.stage);
