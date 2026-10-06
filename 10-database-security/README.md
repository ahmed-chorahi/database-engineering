# 10 · Database Security

> Practical security I can actually apply: who can connect, what they can do, and how not to get hacked by a text box.

Files: [`roles.sql`](roles.sql) · [`sql_injection_demo.py`](sql_injection_demo.py) · [`.env.example`](.env.example)

```text
Authentication  →  "Who are you?"        (password, certificate)
Authorization   →  "What may you do?"    (roles, GRANT/REVOKE)
Auditing        →  "What did you do?"    (logs)
```

## 1. Roles, GRANT, REVOKE (PostgreSQL)

In PostgreSQL users and groups are both **roles**.

```sql
CREATE ROLE report_reader LOGIN PASSWORD 'change_me_1';
GRANT CONNECT ON DATABASE shop TO report_reader;
GRANT USAGE   ON SCHEMA public TO report_reader;
GRANT SELECT  ON ALL TABLES IN SCHEMA public TO report_reader;

REVOKE UPDATE ON orders FROM app_user;       -- take it back
```

Test it (real output):

```text
report_reader> SELECT count(*) FROM customers;      →  6
report_reader> DELETE FROM customers;               →  ERROR:  permission denied for table customers
app_user>      UPDATE orders SET status='paid' ...  →  ERROR:  permission denied for table orders
app_user>      SELECT * FROM employees;             →  ERROR:  permission denied for table employees
```

> ⚠️ **Common mistake:** connecting your app as `postgres` (superuser). One bug or injection and the attacker owns *everything*.

## 2. Least privilege

Give each role **only** what it needs, nothing more.

| Role | Needs | Gets |
|---|---|---|
| `report_reader` | read data | `SELECT` |
| `app_user` | run the app | `SELECT/INSERT/UPDATE` on specific tables |
| `migrator` | change schema | `CREATE`, only during deploys |
| `postgres` | administration | humans only, never the app |

Authentication config lives in `pg_hba.conf` — prefer `scram-sha-256` and never use `trust` outside a toy setup.

## 3. SQL injection

**What:** user input becomes part of the SQL **code**. **Why it matters:** attacker reads/changes/deletes anything the connection can.

### Conceptually

```text
Code:   "SELECT * FROM users WHERE username = '" + input + "' AND password = '" + pw + "'"

Input:  admin' --
Result: SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
                                                    └── everything after -- is a comment!
```

### Run it: [`sql_injection_demo.py`](sql_injection_demo.py)

```text
Attacker types:  admin' --   (password: anything)
  SQL sent: SELECT * FROM users WHERE username = 'admin' --' AND password = 'wrong'
  result: [(2, 'admin', 'topsecret')]            ← logged in as admin, no password!

Attacker types:  ' OR '1'='1
  result: [(1, 'ayesha', 'secret1'), (2, 'admin', 'topsecret')]   ← dumped every user

Same attacks against the SAFE version:
  result: []
  result: []
```
(The demo uses SQLite so it runs anywhere; the idea is identical in PostgreSQL.)

### The safe way: parameterized queries

```python
# ❌ f-string / string concatenation
cur.execute(f"SELECT * FROM users WHERE username = '{name}'")

# ✅ psycopg2 (PostgreSQL) — values are sent separately from the SQL
cur.execute("SELECT * FROM users WHERE username = %s", (name,))
```

The database receives the **query shape** and the **values** separately, so input can never become code.

> ⚠️ Placeholders work for **values**, not table/column names. For dynamic identifiers use an allow-list (`if col in {"name","age"}`) or `psycopg2.sql.Identifier`.

Also: least-privilege roles limit the damage if something slips through.

## 4. Secrets & environment variables

```bash
# .env  (listed in .gitignore!)
DATABASE_URL=postgresql://app_user:CHANGE_ME@localhost:5432/shop
```
```python
import os
url = os.environ["DATABASE_URL"]       # never hard-code passwords in source
```

**Rules:** never commit `.env` · rotate a secret if it ever leaks (even once) · use a secrets manager in production · different passwords per environment.

## 5. Password security

Never store passwords in plain text (my SQL injection demo does — on purpose, as the "bad" example). Store a **salted, slow hash**.

```python
import hashlib, os
salt = os.urandom(16)
hash_ = hashlib.scrypt(b"my password", salt=salt, n=2**14, r=8, p=1)   # store salt + hash
```
In PostgreSQL itself (`pgcrypto`): `SELECT crypt('pw', gen_salt('bf'));`

| ❌ Never | ✅ Use |
|---|---|
| plain text | bcrypt / scrypt / argon2 |
| plain MD5 / SHA-1 | per-user salt |
| same password for DB and app | long random DB passwords |

## 6. Encryption basics

| | Protects against | How |
|---|---|---|
| **In transit** | sniffing on the network | TLS: `sslmode=require` in the connection string |
| **At rest** | stolen disk / backup | disk encryption, encrypted backups |
| **Column-level** | even DBAs seeing values | `pgcrypto`, or encrypt in the app |

## 7. Backups (security view)

- Automate (`pg_dump` nightly + WAL archiving) and **test restores**.
- Encrypt backups and store them *off* the database server.
- Backups contain everything — protect them like the database.
- Follow **3-2-1**: 3 copies, 2 media types, 1 off-site.

## 8. Auditing

| Level | How |
|---|---|
| Connections & slow/DDL statements | `log_connections = on`, `log_statement = 'ddl'` |
| Who changed what | trigger writing to an audit table (see `grade_log` in [02](../02-relational-databases/)) |
| Full-featured | `pgaudit` extension |

```sql
CREATE TABLE audit_log (id SERIAL, who TEXT DEFAULT current_user, what TEXT, at TIMESTAMPTZ DEFAULT now());
```

## ✅ Security checklist

- [ ] App uses a non-superuser role with minimal grants
- [ ] All queries parameterized
- [ ] Secrets in env vars, `.env` git-ignored
- [ ] Passwords hashed with salt (bcrypt/scrypt/argon2)
- [ ] TLS on connections
- [ ] Backups automated, encrypted, **restore-tested**
- [ ] Logging/auditing enabled

## ✏️ Practice

1. Create a role that can read `products` but not `customers`. Prove it.
2. Break `login_safe` on purpose by switching to an f-string, then fix it.
3. Add an `audit_log` trigger to `orders`.

➡️ Next: [11 · Projects](../11-database-engineering-projects/)
