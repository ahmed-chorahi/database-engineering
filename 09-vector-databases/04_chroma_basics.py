"""Part C: Chroma = a vector DATABASE: stores vectors + documents + metadata + ids."""
import chromadb
from chromadb.api.types import EmbeddingFunction
from embed import embed


class MyEmbedder(EmbeddingFunction):             # plug in the same embedder as FAISS
    def __init__(self): pass
    def __call__(self, input):
        return embed(list(input)).tolist()
    @staticmethod
    def name(): return "my-embedder"


client = chromadb.PersistentClient(path="./chroma_store")        # saved on disk
col = client.get_or_create_collection("notes", embedding_function=MyEmbedder())

col.add(
    ids=["n1", "n2", "n3", "n4", "n5"],
    documents=[
        "PostgreSQL is a relational database that uses SQL.",
        "An index makes database queries faster.",
        "MongoDB stores flexible JSON-like documents.",
        "Redis is an in-memory key-value store used for caching.",
        "FAISS performs fast similarity search over vectors.",
    ],
    metadatas=[{"topic": "sql"}, {"topic": "perf"}, {"topic": "nosql"}, {"topic": "nosql"}, {"topic": "vector"}],
)
print("count:", col.count())

# 1. plain similarity search
r = col.query(query_texts=["which database is good for caching?"], n_results=2)
print("\nTop 2:")
for doc, dist in zip(r["documents"][0], r["distances"][0]):
    print(f"  {dist:.3f}  {doc}")

# 2. similarity search + metadata filter
r = col.query(query_texts=["fast storage"], n_results=2, where={"topic": "nosql"})
print("\nOnly topic=nosql:")
for doc in r["documents"][0]:
    print("  ", doc)

# 3. update / delete / get by id
col.update(ids=["n1"], metadatas=[{"topic": "sql", "reviewed": True}])
print("\nget n1:", col.get(ids=["n1"])["metadatas"])
col.delete(ids=["n5"])
print("count after delete:", col.count())
