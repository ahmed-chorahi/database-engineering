# Redis

**What:** an in-memory key-value store. **Why:** reading from RAM is ~1000× faster than disk — perfect for data you read constantly. **Analogy:** sticky notes on your monitor vs. walking to the filing cabinet.

```text
App ──► Redis (RAM, microseconds) ──miss──► PostgreSQL (disk, milliseconds)
```

## Setup

```bash
docker run --name redis -p 6379:6379 -d redis:7
docker exec -it redis redis-cli
```
Python: `pip install redis` → [`redis_demo.py`](redis_demo.py).

## Strings (and counters)

```text
127.0.0.1:6379> SET user:1:name "Ayesha"
OK
127.0.0.1:6379> GET user:1:name
"Ayesha"
127.0.0.1:6379> INCR page:views
(integer) 1
127.0.0.1:6379> INCR page:views
(integer) 2
```
Key naming: `type:id:field` (`user:1:name`) keeps things tidy.

## Lists (ordered, queues)

```text
> RPUSH jobs "email" "resize" "backup"
(integer) 3
> LPOP jobs
"email"
> LRANGE jobs 0 -1
1) "resize"
2) "backup"
```

## Sets (unique, no order)

```text
> SADD online alice bob alice
(integer) 2          ← alice only counted once
> SISMEMBER online bob
(integer) 1
> SMEMBERS online
1) "alice"
2) "bob"
```

## Hashes (a mini-object)

```text
> HSET user:1 name "Ayesha" age 21
(integer) 2
> HGET user:1 name
"Ayesha"
> HGETALL user:1
1) "name"
2) "Ayesha"
3) "age"
4) "21"
```

## TTL — keys that expire

```text
> SET otp:1 "482913" EX 60        ← gone in 60 seconds
OK
> TTL otp:1
(integer) 58
> TTL otp:1                       ← later...
(integer) -2                      ← key no longer exists
```

## Caching: the cache-aside pattern

```text
        ┌─ 1. check Redis ─► HIT  ─► return (fast)
Request ┤
        └─ MISS ─► 2. query PostgreSQL ─► 3. store in Redis with TTL ─► return
```

```python
def get_user(uid):
    cached = r.get(f"user:{uid}")
    if cached:                      # HIT
        return json.loads(cached)
    user = db_query(uid)            # MISS → slow path
    r.set(f"user:{uid}", json.dumps(user), ex=300)   # cache 5 min
    return user
```

> ⚠️ **Common mistakes:** no TTL (stale forever) · caching data that must always be exact (balances) · forgetting to **invalidate** (`DEL user:1`) after an update.

Full hands-on: [Project 5](../11-database-engineering-projects/05-redis-caching/).

## Sessions

Login → store `session:<token>` as a hash with `EX 3600`. Every request looks it up in Redis. Logout = `DEL`. Expiry is free.

## Quick command table

| Task | Command |
|---|---|
| set/get | `SET k v` · `GET k` |
| delete / exists | `DEL k` · `EXISTS k` |
| expire / time left | `EXPIRE k 30` · `TTL k` |
| list keys (dev only!) | `KEYS user:*` |
| wipe (dev only!) | `FLUSHALL` |

## ✏️ Practice

1. Build a rate limiter: `INCR` a key per minute, `EXPIRE` it, block above 5.
2. Store a user as a hash, then read just their `age`.
3. Explain why `KEYS *` is dangerous in production.
