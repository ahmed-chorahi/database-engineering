"""Needs: docker run -p 6379:6379 -d redis:7"""
import redis, time

r = redis.Redis(decode_responses=True)
r.set("greeting", "hello", ex=2)
print(r.get("greeting"), "| ttl:", r.ttl("greeting"))
time.sleep(2.1)
print("after expiry:", r.get("greeting"))

r.hset("user:1", mapping={"name": "Ayesha", "age": 21})
print(r.hgetall("user:1"))
