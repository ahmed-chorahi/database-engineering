"""Project 7: RAG with Chroma. Documents -> chunks -> embeddings -> Chroma -> retrieve -> LLM.
Usage:  python rag.py "Why can too many indexes be bad?"
Set ANTHROPIC_API_KEY to get a real LLM answer; without it the script prints the prompt it WOULD send.
"""
import os, sys, pathlib, chromadb
from chromadb.api.types import EmbeddingFunction
from embed import embed


class Embedder(EmbeddingFunction):
    def __init__(self): pass
    def __call__(self, input): return embed(list(input)).tolist()
    @staticmethod
    def name(): return "project-embedder"


col = chromadb.PersistentClient(path="./chroma_store").get_or_create_collection("knowledge_base", embedding_function=Embedder())


def chunk(text, size=2, overlap=1):
    sents = [s.strip() + "." for s in text.split(".") if s.strip()]
    step = size - overlap
    return [" ".join(sents[i:i + size]) for i in range(0, max(len(sents) - overlap, 1), step)]


def ingest():
    ids, docs, metas = [], [], []
    for path in sorted(pathlib.Path("docs").glob("*.txt")):
        topic = path.stem
        for j, c in enumerate(chunk(path.read_text())):
            ids.append(f"{topic}-{j}"); docs.append(c); metas.append({"topic": topic, "chunk": j})
    col.upsert(ids=ids, documents=docs, metadatas=metas)      # upsert = safe to re-run
    print(f"ingested {len(ids)} chunks")


def retrieve(question, k=3, topic=None):
    where = {"topic": topic} if topic else None               # metadata filter
    r = col.query(query_texts=[question], n_results=k, where=where)
    return list(zip(r["documents"][0], r["metadatas"][0], r["distances"][0]))


def build_prompt(question, hits):
    context = "\n".join(f"[{m['topic']}#{m['chunk']}] {d}" for d, m, _ in hits)
    return f"Answer using ONLY the context. If it isn't there, say you don't know.\n\nContext:\n{context}\n\nQuestion: {question}"


def llm(prompt):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "[no API key set] Prompt that would be sent:\n" + prompt
    import anthropic
    msg = anthropic.Anthropic().messages.create(model="claude-sonnet-4-6", max_tokens=300,
                                                messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text


if __name__ == "__main__":
    if col.count() == 0:
        ingest()
    q = " ".join(sys.argv[1:]) or "Why can too many indexes be bad?"
    hits = retrieve(q)
    print("Retrieved:")
    for d, m, dist in hits:
        print(f"  {dist:.3f} {m['topic']}#{m['chunk']}: {d[:70]}...")
    print("\n" + llm(build_prompt(q, hits)))
