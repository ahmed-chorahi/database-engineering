# Project 5 — Redis Caching (PostgreSQL + Redis)

**Databases:** PostgreSQL + Redis · **File:** [`cache_demo.py`](cache_demo.py) (uses the `ecommerce` DB from Project 2)

## Problem
The "top 5 best-selling products" widget runs a heavy aggregate over 300k rows on every page view.

## Requirements
- Same answer, much faster.
- Data may be up to 60 seconds stale.
- Cache must be invalidatable.

## Choose database
**PostgreSQL** stays the source of truth; **Redis** holds a temporary, expiring copy.

## Design — cache-aside
```text
request ─► Redis GET top_products ─► HIT ─► return
                │ MISS
                └─► PostgreSQL query ─► Redis SET (EX 60) ─► return
```

## Implementation
```python
cached = r.get(key)
if cached: return json.loads(cached), "HIT"
data = top_products_from_db()
r.set(key, json.dumps(data), ex=60)       # TTL = 60 s
return data, "MISS"
```
```bash
docker run -p 6379:6379 -d redis:7
python cache_demo.py
```

## Testing (real run)
```text
1st call: MISS     77.56 ms   ['Product 15', 15175]
2nd call: HIT       0.10 ms
...
ttl left: 58 s
after DELETE -> MISS
```
Proves: first call fills the cache, second is served from it, TTL counts down, `DELETE` forces a refresh.

## Performance (real run, 20 calls each)
| Source | Avg time |
|---|---|
| PostgreSQL | **77.24 ms** |
| Redis cache | **0.061 ms** |
| Speed-up | **~1,267×** |

## What I learned
- Cache expensive, frequently-read, tolerably-stale data — not balances.
- A TTL is the simplest invalidation strategy; explicit `DEL` after writes is the precise one.
- A cache is an optimisation; the app must still work if Redis is empty.
