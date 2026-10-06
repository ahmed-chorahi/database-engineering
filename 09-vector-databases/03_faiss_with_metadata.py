"""FAISS only stores vectors. Metadata (text, source...) is YOUR job: keep a parallel list."""
import numpy as np, faiss
from embed import embed

docs = [
    {"text": "PostgreSQL is a relational database that uses SQL.",         "source": "sql"},
    {"text": "An index makes database queries faster.",                    "source": "perf"},
    {"text": "MongoDB stores flexible JSON-like documents.",               "source": "nosql"},
    {"text": "Redis is an in-memory key-value store used for caching.",    "source": "nosql"},
    {"text": "FAISS performs fast similarity search over vectors.",        "source": "vector"},
]

vecs = embed([d["text"] for d in docs])          # (5, dim), already normalised
index = faiss.IndexFlatIP(vecs.shape[1])         # inner product == cosine (normalised)
index.add(vecs)                                   # row i of the index <-> docs[i]

query = "which database is good for caching?"
D, I = index.search(embed([query]), 3)

print("Query:", query)
for score, i in zip(D[0], I[0]):                  # FAISS returns row numbers; we map back
    print(f"  {score:.3f}  [{docs[i]['source']}]  {docs[i]['text']}")

faiss.write_index(index, "docs.index")            # persist the vectors...
# ...and persist docs yourself (JSON/Postgres). Keep them in the same order!
