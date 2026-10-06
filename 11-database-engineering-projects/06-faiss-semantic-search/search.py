"""Project 6: semantic search over ./docs with FAISS.
Usage:  python search.py "how do I make queries faster?"
"""
import sys, pathlib, json, faiss
from embed import embed

INDEX_FILE, META_FILE = "docs.index", "docs_meta.json"


def chunk(text, size=2, overlap=1):
    sents = [s.strip() + "." for s in text.split(".") if s.strip()]
    step = size - overlap
    return [" ".join(sents[i:i + size]) for i in range(0, max(len(sents) - overlap, 1), step)]


def build():
    chunks, meta = [], []
    for path in sorted(pathlib.Path("docs").glob("*.txt")):
        for j, c in enumerate(chunk(path.read_text())):
            chunks.append(c); meta.append({"file": path.name, "chunk": j, "text": c})
    vecs = embed(chunks)
    index = faiss.IndexFlatIP(vecs.shape[1])      # normalised vectors -> inner product = cosine
    index.add(vecs)
    faiss.write_index(index, INDEX_FILE)
    json.dump(meta, open(META_FILE, "w"))
    print(f"indexed {len(chunks)} chunks from {len(set(m['file'] for m in meta))} files")


def search(query, k=3):
    index = faiss.read_index(INDEX_FILE)
    meta = json.load(open(META_FILE))
    D, I = index.search(embed([query]), k)
    return [(float(s), meta[i]) for s, i in zip(D[0], I[0]) if i != -1]


if __name__ == "__main__":
    if not pathlib.Path(INDEX_FILE).exists():
        build()
    q = " ".join(sys.argv[1:]) or "how do I make queries faster?"
    print(f"\nQ: {q}")
    for score, m in search(q):
        print(f"  {score:.3f}  {m['file']}#{m['chunk']}  {m['text'][:80]}...")
