# Project 7 — Chroma RAG Search

**Databases:** Chroma · **Files:** [`rag.py`](rag.py) · [`docs/`](docs/) · [`embed.py`](embed.py)

## Problem
An LLM doesn't know my documents and will happily make things up. Give it the right chunks to read first (**R**etrieval-**A**ugmented **G**eneration).

## Requirements
- Ingest documents with metadata (`topic`, `chunk`).
- Retrieve top-k chunks, optionally filtered by topic.
- Build a grounded prompt: "answer only from context".
- Safe to re-run ingestion (no duplicates).

## Choose database
**Chroma** — stores vectors *and* text *and* metadata, persists to disk, filters on metadata.

## Design
```text
Question ─► embed ─► Chroma.query(top-3, where=topic?) ─► chunks ─► prompt ─► LLM ─► answer + sources
```

## Implementation
```bash
python rag.py "Why can too many indexes be bad?"      # set ANTHROPIC_API_KEY for a real LLM answer
```
`col.upsert(ids=..., documents=..., metadatas=...)` makes ingestion idempotent.

## Queries (real run, toy embeddings; no API key, so it shows the prompt)
```text
Retrieved:
  1.127 indexes#2: B-tree indexes are the default in PostgreSQL. Too many indexes slow do...
  1.644 mongodb#2: Related data can be embedded inside one document to avoid joins. The a...
  1.653 indexes#1: Without an index the database scans every row. B-tree indexes are the default...

Context:
[indexes#2] B-tree indexes are the default in PostgreSQL. Too many indexes slow down inserts and updates because each index must be maintained.
...
Question: Why can too many indexes be bad?
```
The best chunk is exactly the one containing the answer. The 2nd result is noise from the toy embedder — a real model ranks better.

## Testing
- Ask something *not* in the docs → the prompt tells the LLM to say "I don't know".
- `retrieve(q, topic="redis_cache")` → only Redis chunks.

## Performance
Retrieval takes milliseconds; the LLM call dominates latency. Cache repeated questions (that's Project 8).

## What I learned
- RAG quality = retrieval quality. Bad chunks in → bad answer out.
- Metadata filters narrow the search and make answers citable.
- Chroma returns **distances** (lower is better).
