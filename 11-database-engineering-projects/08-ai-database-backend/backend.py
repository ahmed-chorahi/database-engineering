"""Project 8: one small backend, four databases, each doing what it's best at.

  PostgreSQL -> structured facts (orders, customers)        source of truth
  Chroma     -> knowledge-base chunks for RAG                 meaning-based search
  Redis      -> cache of finished answers (TTL)               speed
  MongoDB    -> chat history documents (optional)             flexible, append-only logs

Usage: python backend.py "How many orders does customer 777 have?"
       python backend.py "Why can too many indexes be bad?"
"""
import os, re, sys, json, hashlib, pathlib, redis, psycopg2, chromadb
from chromadb.api.types import EmbeddingFunction
from embed import embed

# ---------- connections (see CONNECTIONS-STRINGS in the project README) ----------
PG    = psycopg2.connect(os.getenv("DATABASE_URL", "dbname=ecommerce user=postgres host=localhost"))
CACHE = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

class _Emb(EmbeddingFunction):
    def __init__(self): pass
    def __call__(self, input): return embed(list(input)).tolist()
    @staticmethod
    def name(): return "backend-embedder"

KB = chromadb.PersistentClient(path="./chroma_store").get_or_create_collection("knowledge_base", embedding_function=_Emb())

try:                                             # MongoDB is optional: skip logging if it's not running
    from pymongo import MongoClient
    LOG = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=500)["ai_backend"]["chats"]
    LOG.database.client.admin.command("ping")
except Exception:
    LOG = None


# ---------- knowledge base ----------
def ingest():
    ids, docs, metas = [], [], []
    for p in sorted(pathlib.Path("docs").glob("*.txt")):
        sents = [s.strip() + "." for s in p.read_text().split(".") if s.strip()]
        for j in range(0, len(sents), 2):
            ids.append(f"{p.stem}-{j}"); docs.append(" ".join(sents[j:j + 2])); metas.append({"topic": p.stem})
    KB.upsert(ids=ids, documents=docs, metadatas=metas)


# ---------- the router: structured question or knowledge question? ----------
def structured_answer(question):
    """Tiny rule-based 'text-to-SQL'. Parameterised SQL only - never paste user text into SQL.
    (Section 12 shows how an LLM generates the SQL instead.)"""
    m = re.search(r"orders.*customer (\d+)|customer (\d+).*orders", question.lower())
    if not m:
        return None
    cid = int(m.group(1) or m.group(2))
    with PG.cursor() as cur:
        cur.execute("SELECT COUNT(*), COALESCE(SUM(p.amount),0) FROM orders o LEFT JOIN payments p ON p.order_id=o.id WHERE o.customer_id=%s", (cid,))
        n, paid = cur.fetchone()
    return f"Customer {cid} has {n} orders and has paid {paid:.2f} in total."


def knowledge_context(question, k=3):
    r = KB.query(query_texts=[question], n_results=k)
    return r["documents"][0]


def llm(prompt):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "[no API key] would send prompt:\n" + prompt
    import anthropic
    m = anthropic.Anthropic().messages.create(model="claude-sonnet-4-6", max_tokens=300,
                                              messages=[{"role": "user", "content": prompt}])
    return m.content[0].text


def ask(user_id, question):
    key = "answer:" + hashlib.sha256(question.strip().lower().encode()).hexdigest()[:16]
    cached = CACHE.get(key)                                  # 1. Redis
    if cached:
        return cached, "cache HIT"

    facts = structured_answer(question)                      # 2. PostgreSQL
    if facts:
        answer, source = facts, "postgres"
    else:                                                    # 3. Chroma -> LLM
        ctx = "\n".join(knowledge_context(question))
        answer = llm(f"Answer ONLY from this context, else say you don't know.\n\n{ctx}\n\nQuestion: {question}")
        source = "chroma+llm"

    if not answer.startswith("[no API key]"):                # don't cache the offline stub
        CACHE.set(key, answer, ex=300)                       # cache for 5 minutes
    if LOG is not None:                                      # 4. MongoDB history
        LOG.insert_one({"user": user_id, "question": question, "answer": answer, "source": source})
    return answer, source


if __name__ == "__main__":
    if KB.count() == 0:
        ingest()
    q = " ".join(sys.argv[1:]) or "How many orders does customer 777 have?"
    for attempt in (1, 2):                                   # ask twice to see the cache work
        ans, src = ask("student-1", q)
        print(f"[{attempt}] ({src}) {ans[:300]}\n")
