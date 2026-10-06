"""Cache-aside: PostgreSQL (slow, source of truth) + Redis (fast, temporary copy).
Needs: the `ecommerce` database from Project 2, and Redis on localhost:6379."""
import json, time, redis, psycopg2

DSN = "dbname=ecommerce user=postgres host=localhost"
pg = psycopg2.connect(DSN)
r = redis.Redis(decode_responses=True)
TTL = 60  # seconds


def top_products_from_db():
    """A deliberately heavy query: best-selling products over 300k order lines."""
    with pg.cursor() as cur:
        cur.execute("""
            SELECT p.name, SUM(oi.quantity) AS sold
            FROM order_items oi JOIN products p ON p.id = oi.product_id
            GROUP BY p.name ORDER BY sold DESC LIMIT 5""")
        return [[name, int(sold)] for name, sold in cur.fetchall()]


def top_products():
    key = "top_products"
    cached = r.get(key)
    if cached:                                   # 1. HIT  -> return immediately
        return json.loads(cached), "HIT"
    data = top_products_from_db()                # 2. MISS -> ask PostgreSQL
    r.set(key, json.dumps(data), ex=TTL)         # 3. store with TTL
    return data, "MISS"


def timed(fn):
    t = time.perf_counter(); out = fn(); return out, (time.perf_counter() - t) * 1000


if __name__ == "__main__":
    r.delete("top_products")
    (data, status), ms = timed(top_products);  print(f"1st call: {status:4}  {ms:8.2f} ms   {data[0]}")
    (data, status), ms = timed(top_products);  print(f"2nd call: {status:4}  {ms:8.2f} ms")

    N = 20
    t = time.perf_counter()
    for _ in range(N): top_products_from_db()
    db_ms = (time.perf_counter() - t) * 1000 / N

    t = time.perf_counter()
    for _ in range(N): top_products()
    cache_ms = (time.perf_counter() - t) * 1000 / N

    print(f"\naverage over {N} calls:  PostgreSQL {db_ms:.2f} ms   |   Redis cache {cache_ms:.3f} ms   |   {db_ms/cache_ms:.0f}x faster")

    # TTL + invalidation
    print("ttl left:", r.ttl("top_products"), "s")
    r.delete("top_products")        # invalidate after data changes
    print("after DELETE ->", top_products()[1])
