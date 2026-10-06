"""Text-to-SQL, the careful way.
LLM writes SQL  ->  we VALIDATE it  ->  run it with a READ-ONLY role  ->  LLM explains the rows.

Run the safety self-test (no LLM/API key needed):   python text_to_sql.py
Run for real:  ANTHROPIC_API_KEY=... python text_to_sql.py "Which customers never ordered?"
"""
import os, re, sys

# 1. Give the LLM the schema (its only knowledge of your database)
SCHEMA = """
customers(id, name, email, city, joined_on)
products(id, name, category, price)
orders(id, customer_id -> customers.id, order_date, status)   -- status: pending|paid|shipped|cancelled
order_items(id, order_id -> orders.id, product_id -> products.id, quantity)
"""

PROMPT = """You are a PostgreSQL expert. Write ONE read-only SELECT query that answers the question.
Use only these tables:
{schema}
Rules: SELECT only, no semicolons, always include LIMIT 50. Return ONLY the SQL.
Question: {question}"""

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|call|do|pg_sleep)\b", re.I)


# 2. Never trust generated SQL
def validate(sql: str) -> str:
    sql = sql.strip().rstrip(";")
    if ";" in sql:                          raise ValueError("multiple statements")
    if not re.match(r"^(select|with)\b", sql, re.I): raise ValueError("must start with SELECT/WITH")
    if FORBIDDEN.search(sql):               raise ValueError("forbidden keyword")
    if "--" in sql or "/*" in sql:          raise ValueError("comments not allowed")
    if not re.search(r"\blimit\s+\d+", sql, re.I):
        sql += " LIMIT 50"                  # cap the result size
    return sql


def generate_sql(question: str) -> str:
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model="claude-sonnet-4-6", max_tokens=300,
        messages=[{"role": "user", "content": PROMPT.format(schema=SCHEMA, question=question)}])
    return msg.content[0].text.strip().strip("`").removeprefix("sql").strip()


def run_query(sql: str):
    import psycopg2
    # connect as a role that only has SELECT (see 10-database-security/roles.sql) - the REAL safety net
    conn = psycopg2.connect(os.getenv("READONLY_DSN", "dbname=shop user=report_reader password=change_me_1 host=localhost"))
    conn.set_session(readonly=True)
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout = 3000")           # kill runaway queries
        cur.execute(sql)
        return [d[0] for d in cur.description], cur.fetchall()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        sql = validate(generate_sql(q))
        print("SQL:", sql)
        cols, rows = run_query(sql)
        print(cols); [print(r) for r in rows]
    else:                                                      # self-test of the validator
        tests = {
            "SELECT name FROM customers": True,
            "SELECT * FROM orders; DROP TABLE orders": False,
            "DELETE FROM customers": False,
            "SELECT 1 -- ' OR 1=1": False,
            "WITH t AS (SELECT 1) SELECT * FROM t": True,
        }
        for sql, should_pass in tests.items():
            try:
                out = validate(sql); ok = should_pass
                print(f"{'PASS' if ok else 'FAIL'}  allowed : {out}")
            except ValueError as e:
                ok = not should_pass
                print(f"{'PASS' if ok else 'FAIL'}  blocked ({e}): {sql}")
