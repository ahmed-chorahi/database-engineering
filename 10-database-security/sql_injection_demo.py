"""SQL injection, shown safely on a throwaway SQLite database (no server needed)."""
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT);
INSERT INTO users (username, password) VALUES ('ayesha', 'secret1'), ('admin', 'topsecret');
""")

def login_unsafe(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print("  SQL sent:", query)
    return db.execute(query).fetchall()

def login_safe(username, password):
    query = "SELECT * FROM users WHERE username = ? AND password = ?"   # placeholders
    return db.execute(query, (username, password)).fetchall()

print("Normal login (unsafe version):")
print("  result:", login_unsafe("ayesha", "secret1"))

print("\nAttacker types:  admin' --   (password: anything)")
print("  result:", login_unsafe("admin' --", "wrong"))     # logs in as admin without a password!

print("\nAttacker types:  ' OR '1'='1")
print("  result:", login_unsafe("x", "' OR '1'='1"))        # returns every user

print("\nSame attacks against the SAFE version:")
print("  result:", login_safe("admin' --", "wrong"))
print("  result:", login_safe("x", "' OR '1'='1"))
