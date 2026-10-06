# Project 6 — FAISS Semantic Search

**Databases:** FAISS · **Files:** [`search.py`](search.py) · [`docs/`](docs/) · [`embed.py`](embed.py)

## Problem
Keyword search misses meaning: "speed up my queries" should find the doc about *indexes* even without the word "indexes".

## Requirements
- Index a folder of text files.
- Return the top-k most relevant chunks with file name and score.
- Save the index to disk.

## Choose database
**FAISS** — a fast in-process vector search library; I'll manage the metadata myself.

## Design
```text
docs/*.txt → chunk (2 sentences, 1 overlap) → embed → faiss.IndexFlatIP (cosine)
                          └── metadata.json  (row i  ↔  {file, chunk, text})
```

## Implementation
```bash
pip install faiss-cpu numpy sentence-transformers
python search.py "how do I speed up a slow query with an index"
```

## Queries — (real run, **toy embeddings**; install `sentence-transformers` for real semantic matching)
```text
indexed 19 chunks from 6 files

Q: how do I speed up a slow query with an index
  0.386  indexes.txt#0  An index is a data structure that speeds up lookups. Without an index the databa...
  0.329  embeddings.txt#1  Texts with similar meaning end up close together in vector space. ...
  0.311  postgres_basics.txt#0  PostgreSQL is a relational database. Data lives in tables ...
```

## Testing
Ask 5 questions where you know the answer file. Count how often it's ranked #1. With the real model, queries that share *no words* with the doc should still match.

## Performance
Flat (exact) search over thousands of chunks is instant. Past ~1M vectors try `IndexIVFFlat` or `IndexHNSWFlat` (see [09](../../09-vector-databases/)).

## What I learned
- Chunk size matters: too big blurs meaning, too small loses context.
- FAISS returns row numbers — keeping `metadata[i]` aligned with the index is *my* responsibility.
- Normalise vectors before using inner product.
