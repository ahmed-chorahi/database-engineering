"""Safe money transfer + concurrency stress test.
Run:  psql -U postgres -f schema.sql  &&  python transfer.py
"""
import random, threading, psycopg2

DSN = "dbname=banking user=postgres host=localhost"   # edit for your setup


def transfer(conn, src, dst, amount):
    """Move money atomically. Returns True/False. Never leaves half a transfer behind."""
    try:
        with conn.cursor() as cur:
            # Lock BOTH rows in id order -> two opposite transfers can never deadlock
            first, second = sorted([src, dst])
            cur.execute("SELECT id FROM accounts WHERE id IN (%s,%s) ORDER BY id FOR UPDATE", (first, second))
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, src))  # CHECK blocks overdraft
            cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, dst))
            cur.execute("INSERT INTO transfers (from_acct,to_acct,amount) VALUES (%s,%s,%s)", (src, dst, amount))
        conn.commit()
        return True
    except psycopg2.errors.CheckViolation:     # not enough money
        conn.rollback()
        return False


def worker(n, stats):
    conn = psycopg2.connect(DSN)
    for _ in range(n):
        a, b = random.sample(range(1, 6), 2)
        ok = transfer(conn, a, b, random.randint(50, 600))
        stats["ok" if ok else "rejected"] += 1


def total():
    with psycopg2.connect(DSN) as c, c.cursor() as cur:
        cur.execute("SELECT SUM(balance) FROM accounts"); return cur.fetchone()[0]


if __name__ == "__main__":
    print("total money before:", total())
    stats = {"ok": 0, "rejected": 0}
    threads = [threading.Thread(target=worker, args=(100, stats)) for _ in range(8)]   # 8 clients x 100 transfers
    [t.start() for t in threads]; [t.join() for t in threads]
    print("transfers:", stats)
    print("total money after :", total())
    with psycopg2.connect(DSN) as c, c.cursor() as cur:
        cur.execute("SELECT count(*) FROM accounts WHERE balance < 0"); print("negative balances:", cur.fetchone()[0])
