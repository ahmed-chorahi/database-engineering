DROP DATABASE IF EXISTS ecommerce;
CREATE DATABASE ecommerce;
\c ecommerce

-- 3NF design: customers / addresses / categories / products / orders / order_items / payments
CREATE TABLE customers  (id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE categories (id SERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE products   (id SERIAL PRIMARY KEY, name TEXT NOT NULL, category_id INT NOT NULL REFERENCES categories(id),
                         price NUMERIC(10,2) NOT NULL CHECK (price > 0), stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0));
CREATE TABLE orders     (id SERIAL PRIMARY KEY, customer_id INT NOT NULL REFERENCES customers(id),
                         status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','paid','shipped','cancelled')),
                         created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE order_items(order_id INT REFERENCES orders(id) ON DELETE CASCADE, product_id INT REFERENCES products(id),
                         quantity INT NOT NULL CHECK (quantity > 0),
                         unit_price NUMERIC(10,2) NOT NULL,         -- price AT PURCHASE TIME (prices change later!)
                         PRIMARY KEY (order_id, product_id));
CREATE TABLE payments   (id SERIAL PRIMARY KEY, order_id INT NOT NULL REFERENCES orders(id),
                         amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
                         method TEXT NOT NULL CHECK (method IN ('card','cash','wallet')),
                         paid_at TIMESTAMPTZ NOT NULL DEFAULT now());

-- Sample data: 2,000 customers, 50 products, 100,000 orders, ~250,000 items (so indexing matters)
INSERT INTO categories (name) SELECT 'Category ' || g FROM generate_series(1,5) g;
INSERT INTO products (name, category_id, price, stock)
SELECT 'Product ' || g, 1 + g % 5, (5 + random()*500)::numeric(10,2), 100 FROM generate_series(1,50) g;
INSERT INTO customers (name, email) SELECT 'Customer ' || g, 'c' || g || '@mail.com' FROM generate_series(1,2000) g;
INSERT INTO orders (customer_id, status, created_at)
SELECT 1 + (random()*1999)::int, (ARRAY['pending','paid','shipped','cancelled'])[1 + (random()*3)::int],
       now() - (random()*365 || ' days')::interval FROM generate_series(1,100000);
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT o.id, p.id, 1 + (random()*3)::int, p.price
FROM orders o
CROSS JOIN generate_series(1,3) k                      -- 3 items per order
JOIN products p ON p.id = 1 + ((o.id * 7919 + k * 17) % 50);   -- spreads orders across products
INSERT INTO payments (order_id, amount, method)
SELECT o.id, SUM(oi.quantity*oi.unit_price), (ARRAY['card','cash','wallet'])[1 + (random()*2)::int]
FROM orders o JOIN order_items oi ON oi.order_id=o.id WHERE o.status IN ('paid','shipped') GROUP BY o.id;
ANALYZE;
