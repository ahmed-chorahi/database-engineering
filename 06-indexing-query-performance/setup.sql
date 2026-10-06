-- 500k fake orders to make performance differences visible
DROP DATABASE IF EXISTS perf;
CREATE DATABASE perf;
\c perf
CREATE TABLE big_orders (
    id          SERIAL PRIMARY KEY,
    customer_id INT  NOT NULL,
    status      TEXT NOT NULL,
    amount      NUMERIC(8,2) NOT NULL,
    created_at  DATE NOT NULL
);
INSERT INTO big_orders (customer_id, status, amount, created_at)
SELECT (random()*50000)::int + 1,
       (ARRAY['pending','paid','shipped','cancelled'])[1 + (random()*3)::int],
       (random()*1000)::numeric(8,2),
       DATE '2023-01-01' + (random()*700)::int
FROM generate_series(1, 500000);
ANALYZE big_orders;
