-- Practice database: a tiny online shop
-- Run:  psql -U postgres -f schema.sql   (then seed.sql)

DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
\c shop

CREATE TABLE customers (
    id        SERIAL PRIMARY KEY,
    name      TEXT NOT NULL,
    email     TEXT UNIQUE,
    city      TEXT,
    joined_on DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE products (
    id       SERIAL PRIMARY KEY,
    name     TEXT NOT NULL,
    category TEXT NOT NULL,
    price    NUMERIC(8,2) NOT NULL CHECK (price > 0)
);

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(id),
    order_date  DATE NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','paid','shipped','cancelled'))
);

CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INT NOT NULL REFERENCES orders(id),
    product_id INT NOT NULL REFERENCES products(id),
    quantity   INT NOT NULL CHECK (quantity > 0)
);

CREATE TABLE employees (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    dept       TEXT NOT NULL,
    salary     NUMERIC(9,2) NOT NULL,
    manager_id INT REFERENCES employees(id)   -- self reference
);
