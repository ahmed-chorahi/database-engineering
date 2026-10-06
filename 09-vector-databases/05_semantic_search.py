"""Part D: a small semantic-search project.
Documents -> Chunking -> Embedding -> Vectors -> FAISS / Chroma -> Top-K results
"""
import numpy as np, faiss
from embed import embed

# 1. Documents (imagine these are long files)
documents = {
    "databases.txt": (
        "A relational database stores data in tables with rows and columns. "
        "SQL is used to query it. Indexes speed up lookups by avoiding full table scans. "
        "Transactions make sure a group of changes either all succeed or all fail."
    ),
    "nosql.txt": (
        "MongoDB keeps data as flexible documents. Redis keeps data in memory for very fast access. "
        "Caching with Redis reduces load on the main database."
    ),
    "vectors.txt": (
        "An embedding turns text into a list of numbers. Similar meanings give nearby vectors. "
        "FAISS searches vectors quickly. Chroma stores vectors together with documents and metadata."
    ),
}

# 2. Chunking: split text into small overlapping pieces (3 sentences, overlap 1)
def chunk(text, size=3, overlap=1):
    sents = [s.strip() + "." for s in text.split(".") if s.strip()]
    step = size - overlap
    return [" ".join(sents[i:i + size]) for i in range(0, max(len(sents) - overlap, 1), step)]

chunks, meta = [], []
for name, text in documents.items():
    for j, c in enumerate(chunk(text)):
        chunks.append(c)
        meta.append({"file": name, "chunk": j})
print(f"{len(documents)} documents -> {len(chunks)} chunks")

# 3. Embed + 4. Index
vecs = embed(chunks)
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs)

# 5. Search
def search(q, k=3):
    D, I = index.search(embed([q]), k)
    return [(float(D[0][r]), meta[i], chunks[i]) for r, i in enumerate(I[0])]

for q in ["how do I make queries faster?", "what stores vectors and metadata?"]:
    print(f"\nQ: {q}")
    for score, m, text in search(q):
        print(f"  {score:.3f} {m['file']}#{m['chunk']}: {text[:70]}...")
