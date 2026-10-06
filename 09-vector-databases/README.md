# 09 · Vector Databases & Similarity Search

> The section that connects databases to AI. SQL asks *"which rows equal X?"* — vectors ask *"which things **mean** something like X?"*

```text
Part A  Fundamentals (NumPy)   →  01_similarity_numpy.py
Part B  FAISS                  →  02_faiss_basics.py, 03_faiss_with_metadata.py
Part C  Chroma                 →  04_chroma_basics.py
Part D  Semantic search        →  05_semantic_search.py
```

```bash
pip install numpy faiss-cpu chromadb sentence-transformers
python 01_similarity_numpy.py
```

> 📝 **About `embed.py`:** every script gets its embeddings from this one file. It uses a real model (`all-MiniLM-L6-v2`) when `sentence-transformers` is installed. If not, it falls back to a toy word-hash embedding so the code still runs offline. **The outputs below are from the toy fallback**, so they only match shared *words*. With the real model the same code understands meaning ("cheap" ≈ "affordable"). Run it both ways and compare — that was my "aha" moment.

---

## Part A — Vector fundamentals

### Embedding, vector, dimension

- **Vector** – a list of numbers: `[0.9, 0.1, 0.0]`.
- **Embedding** – a vector produced by a model so that **similar meaning → nearby vectors**.
- **Dimension** – how many numbers. Real models: 384, 768, 1536...

*Analogy:* GPS coordinates. Two cafés with close coordinates are close in space; two sentences with close embeddings are close in *meaning*.

```text
        ▲ dim 2
        │      • kitten
        │     • cat          (close together = similar)
        │
        │                          • car     (far away = different)
        └──────────────────────────────► dim 1
```

### Three ways to measure "close"

| Metric | Formula idea | Bigger means | Notes |
|---|---|---|---|
| **Dot product** | `Σ aᵢ·bᵢ` | more similar | affected by vector length |
| **Euclidean (L2)** | `√Σ (aᵢ−bᵢ)²` | **less** similar (it's a distance) | straight-line distance |
| **Cosine similarity** | `dot / (‖a‖·‖b‖)` | more similar (−1 to 1) | compares *direction* only — the usual choice for text |

If vectors are **normalised** (length 1), cosine = dot product. That's why we normalise before using FAISS's inner-product index.

### Run it from scratch — `01_similarity_numpy.py`

```text
pair               dot   euclid   cosine
cat-kitten       0.740    0.173    0.984
cat-car          0.020    1.277    0.024

query -> [('cat', 0.996), ('kitten', 0.996), ('car', 0.094)]
```

`cat` and `kitten` are near (cosine ≈ 1); `car` is far (≈ 0).

### Nearest-neighbour search

**Exact (brute force / kNN):** compare the query with *every* vector, sort, take top-k. Perfect, but 10 million vectors × every query = slow.

**Approximate (ANN):** use a clever structure to check only the *promising* vectors. Slightly less accurate, vastly faster.

| | Exact | Approximate |
|---|---|---|
| Accuracy | 100% | ~95–99% |
| Speed on big data | slow | fast |
| FAISS | `IndexFlatL2` | `IndexIVFFlat`, `IndexHNSWFlat` |

> ⚠️ **Common mistake:** mixing embeddings from two different models in one index. Their numbers live in different "spaces" — comparisons are meaningless.

---

## Part B — FAISS

1. **What:** *Facebook AI Similarity Search* — a C++ library (with Python bindings) for fast vector search.
2. **Why:** brute-force NumPy doesn't scale; FAISS is highly optimised, supports ANN and GPUs.
3. **Analogy:** a super-fast search *engine* with no filing system — it gives you row numbers, nothing else.

### The whole API in 6 lines — `02_faiss_basics.py`

```python
import numpy as np, faiss
d = 64
data  = np.random.random((10_000, d)).astype("float32")   # must be float32
index = faiss.IndexFlatL2(d)        # build index (L2 distance)
index.add(data)                     # add vectors
D, I = index.search(data[:1] + 0.01, 3)   # top-3: Distances, Ids
```

```text
vectors in index: 10000
L2  ids: [   0  612 7895] distances: [0.006 4.848 5.285]
IP  ids: [   0  612 3566] scores:    [1.    0.894 0.887]
reloaded: 10000 vectors
IVF ids: [   0 7895 1112] (approximate)
```

- The query was vector 0 with a tiny change → it finds `0` first with distance ≈ 0. ✅
- **L2:** smaller = closer. **Inner product:** bigger = closer.
- `IndexFlatL2` = exact. `IndexIVFFlat` = approximate (cluster first, search only `nprobe` clusters).
- `faiss.write_index(index, "x.index")` / `faiss.read_index("x.index")` saves/loads.

### Index cheat sheet

| Index | Type | Use when |
|---|---|---|
| `IndexFlatL2` / `IndexFlatIP` | exact | < ~1M vectors, or you need perfect recall |
| `IndexIVFFlat` | approximate (clusters) | millions of vectors, needs `train()` |
| `IndexHNSWFlat` | approximate (graph) | fast queries, high accuracy, more RAM |

### Metadata handling — `03_faiss_with_metadata.py`

**FAISS stores only vectors.** Row *i* in the index ↔ item *i* in your own list/DB:

```python
D, I = index.search(embed([query]), 3)
for score, i in zip(D[0], I[0]):
    print(score, docs[i]["source"], docs[i]["text"])    # map ids back yourself
```
```text
Query: which database is good for caching?
  0.408  [nosql]  Redis is an in-memory key-value store used for caching.
  0.289  [sql]  PostgreSQL is a relational database that uses SQL.
  0.183  [nosql]  MongoDB stores flexible JSON-like documents.
```

> ⚠️ **Common mistakes:** passing `float64` arrays · forgetting `faiss.normalize_L2` before an inner-product index · changing the order of your `docs` list after building the index · treating `-1` ids as real results (FAISS returns `-1` when it finds fewer than k).

**Use FAISS when:** you want raw speed/control, vectors fit in your app, and you'll manage storage and metadata yourself.

---

## Part C — Chroma

1. **What:** an open-source **vector database**: stores embeddings **plus** the documents, metadata and ids.
2. **Why:** FAISS gives row numbers; Chroma gives you *"here's the document, its source, its score"* and filtering — what RAG needs.
3. **Analogy:** FAISS = engine, Chroma = the whole car.

### Vocabulary

| Term | Meaning |
|---|---|
| **Collection** | like a table: a group of embeddings |
| **id** | your unique id per item (`"n1"`) |
| **document** | the original text |
| **embedding** | the vector (Chroma creates it, or you provide it) |
| **metadata** | a dict of extra info for filtering (`{"topic": "nosql"}`) |

### Core flow — `04_chroma_basics.py`

```python
import chromadb
client = chromadb.PersistentClient(path="./chroma_store")     # persists to disk
col = client.get_or_create_collection("notes")

col.add(ids=["n1","n2"],
        documents=["Redis is an in-memory key-value store.", "PostgreSQL uses SQL."],
        metadatas=[{"topic":"nosql"}, {"topic":"sql"}])

col.query(query_texts=["which database is good for caching?"], n_results=2)
col.query(query_texts=["fast storage"], n_results=2, where={"topic": "nosql"})   # filter
```

```text
Top 2:
  1.184  Redis is an in-memory key-value store used for caching.
  1.423  PostgreSQL is a relational database that uses SQL.

Only topic=nosql:
   MongoDB stores flexible JSON-like documents.
   Redis is an in-memory key-value store used for caching.
```

Chroma returns **distances** (smaller = closer), not similarities.

Other handy calls: `col.get(ids=[...])`, `col.update(...)`, `col.delete(ids=[...])`, `col.count()`.

> ⚠️ **Common mistakes:** duplicate ids · switching embedding model after data is stored · expecting a higher score to be better (it's a distance) · using `Client()` (in-memory) and wondering why data vanished — use `PersistentClient`.

> By default Chroma downloads its own small embedding model. I pass `embed.py`'s function instead so FAISS and Chroma use identical vectors.

### Basic RAG with Chroma

```text
Question ─► embed ─► Chroma top-3 chunks ─► put chunks in the prompt ─► LLM ─► grounded answer
```

```python
hits = col.query(query_texts=[question], n_results=3)["documents"][0]
prompt = "Answer using ONLY this context:\n" + "\n".join(hits) + f"\n\nQuestion: {question}"
# answer = llm(prompt)
```
Full version: [Project 7](../11-database-engineering-projects/07-chroma-rag-search/).

### FAISS vs Chroma

```text
FAISS
↓
Fast vector similarity/search library
(vectors in, row numbers out; you manage everything else)

Chroma
↓
Vector database focused on storing,
managing, and querying embeddings
(vectors + documents + metadata + persistence + filtering)
```

| | FAISS | Chroma |
|---|---|---|
| Type | library | database |
| Stores documents/metadata | ❌ you do | ✅ |
| Metadata filtering | ❌ | ✅ `where={...}` |
| Persistence | manual files | built in |
| Speed at huge scale / ANN options | ⭐ best | good |
| Learning value | how search works | how RAG apps work |
| Use for | benchmarks, big offline indexes | prototypes, RAG apps |

---

## Part D — Semantic search project — `05_semantic_search.py`

```text
Documents ─► Chunking ─► Embedding Model ─► Vectors ─► FAISS / Chroma ─► Similarity Search ─► Top-K
```

**Chunking:** embeddings of a whole book are mush. Split into small overlapping pieces so each chunk holds one idea (overlap keeps sentences from being cut off from their context).

```python
def chunk(text, size=3, overlap=1):           # 3 sentences per chunk, 1 shared with the next
    sents = [s.strip() + "." for s in text.split(".") if s.strip()]
    step = size - overlap
    return [" ".join(sents[i:i+size]) for i in range(0, max(len(sents)-overlap, 1), step)]
```

```text
3 documents -> 5 chunks

Q: what stores vectors and metadata?
  0.598 vectors.txt#1: FAISS searches vectors quickly. Chroma stores vectors together with do...
  0.183 vectors.txt#0: An embedding turns text into a list of numbers. Similar meanings give ...
  0.163 databases.txt#0: A relational database stores data in tables with rows and columns. SQL...
```

Best match first, with the file name and chunk number — exactly what you'd cite in a RAG answer.

## SQL vs vector search

| | SQL `WHERE` | Vector search |
|---|---|---|
| Finds | exact matches | similar meaning |
| "cheap laptops" finds "affordable notebooks"? | ❌ | ✅ |
| Result | exact | ranked by score |

## ✏️ Practice

1. Add two more vectors to `01_similarity_numpy.py` and rank them.
2. In `02_faiss_basics.py` change `nprobe` to 1, then 50. Watch accuracy vs speed.
3. Install `sentence-transformers`, re-run `05_semantic_search.py`, and compare to the toy output.
4. Add a `where` filter to the semantic search so only `nosql.txt` is searched.

➡️ Next: [10 · Database Security](../10-database-security/)
