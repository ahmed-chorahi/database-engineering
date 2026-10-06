\c ecommerce
\timing off
EXPLAIN ANALYZE SELECT o.id, o.status FROM orders o WHERE o.customer_id = 777 ORDER BY o.created_at DESC;
CREATE INDEX idx_orders_customer_created ON orders (customer_id, created_at DESC);
EXPLAIN ANALYZE SELECT o.id, o.status FROM orders o WHERE o.customer_id = 777 ORDER BY o.created_at DESC;
CREATE INDEX idx_payments_order ON payments (order_id);   -- FK columns are NOT indexed automatically in PostgreSQL!
