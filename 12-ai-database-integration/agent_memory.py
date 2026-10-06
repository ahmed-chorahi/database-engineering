"""Database-backed agent memory.
  PostgreSQL  = short-term memory: the exact conversation log, in order  (structured)
  Chroma      = long-term memory: facts worth remembering, found by MEANING (vectors)

Run:  python agent_memory.py
"""
import psycopg2, chromadb, uuid
from chromadb.api.types import EmbeddingFunction
from embed import embed

pg = psycopg2.connect("dbname=postgres user=postgres host=localhost")
pg.autocommit = True
with pg.cursor() as cur:
    cur.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
        id SERIAL PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL CHECK (role IN ('user','assistant')),
        content TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages (session_id, id)")


class _Emb(EmbeddingFunction):
    def __init__(self): pass
    def __call__(self, input): return embed(list(input)).tolist()
    @staticmethod
    def name(): return "memory-embedder"

memory = chromadb.EphemeralClient().get_or_create_collection("long_term_memory", embedding_function=_Emb())


# ---- short-term: last N messages from PostgreSQL
def log(session, role, content):
    with pg.cursor() as cur:
        cur.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (%s,%s,%s)", (session, role, content))

def recent(session, n=4):
    with pg.cursor() as cur:
        cur.execute("SELECT role, content FROM (SELECT * FROM chat_messages WHERE session_id=%s ORDER BY id DESC LIMIT %s) t ORDER BY id", (session, n))
        return cur.fetchall()


# ---- long-term: remember a fact, recall by meaning
def remember(user, fact):
    memory.add(ids=[str(uuid.uuid4())], documents=[fact], metadatas=[{"user": user}])

def recall(user, query, k=2):
    r = memory.query(query_texts=[query], n_results=k, where={"user": user})   # metadata filter = privacy boundary
    return r["documents"][0]


def build_prompt(user, session, question):
    facts = "\n".join("- " + f for f in recall(user, question))
    history = "\n".join(f"{r}: {c}" for r, c in recent(session))
    return f"Things I remember about {user}:\n{facts}\n\nRecent conversation:\n{history}\n\nuser: {question}"


if __name__ == "__main__":
    remember("ayesha", "Ayesha is studying database engineering and prefers PostgreSQL.")
    remember("ayesha", "Ayesha is allergic to peanuts.")
    remember("bilal",  "Bilal prefers MongoDB for side projects.")

    sess = "demo-" + uuid.uuid4().hex[:6]
    log(sess, "user", "Hi!"); log(sess, "assistant", "Hello Ayesha, how can I help?")
    print(build_prompt("ayesha", sess, "Which database should I use for my study project?"))
