"""Two sessions fighting over the same rows. Run: python concurrency_demo.py
Needs the `bank` database from setup.sql."""
import threading, time, psycopg2

DSN = "dbname=bank user=postgres host=localhost"   # change for your setup

def conn(level=None):
    c = psycopg2.connect(DSN)
    if level: c.set_session(isolation_level=level)
    return c

# ---------- 1. Non-repeatable read (READ COMMITTED) vs snapshot (REPEATABLE READ)
def read_twice(level):
    a, b = conn(level), conn()
    ca = a.cursor()
    ca.execute("SELECT balance FROM accounts WHERE id=1"); first = ca.fetchone()[0]
    cb = b.cursor(); cb.execute("UPDATE accounts SET balance = balance + 50 WHERE id=1"); b.commit()
    ca.execute("SELECT balance FROM accounts WHERE id=1"); second = ca.fetchone()[0]
    a.rollback()
    cb.execute("UPDATE accounts SET balance = balance - 50 WHERE id=1"); b.commit()  # undo
    return first, second

print("READ COMMITTED  :", read_twice("READ COMMITTED"))
print("REPEATABLE READ :", read_twice("REPEATABLE READ"))

# ---------- 2. Deadlock: two transactions lock rows in opposite order
def transfer(first_id, second_id, label, results):
    c = conn(); cur = c.cursor()
    try:
        cur.execute("UPDATE accounts SET balance = balance WHERE id=%s", (first_id,))
        time.sleep(0.5)                       # let the other one grab its first lock
        cur.execute("UPDATE accounts SET balance = balance WHERE id=%s", (second_id,))
        c.commit(); results[label] = "committed"
    except psycopg2.errors.DeadlockDetected:
        c.rollback(); results[label] = "DEADLOCK -> rolled back"

res = {}
t1 = threading.Thread(target=transfer, args=(1, 2, "T1 (1 then 2)", res))
t2 = threading.Thread(target=transfer, args=(2, 1, "T2 (2 then 1)", res))
t1.start(); t2.start(); t1.join(); t2.join()
print(res)
