\c ecommerce
\timing on
-- Q1: revenue per category (joins 4 tables)
SELECT c.name, SUM(oi.quantity*oi.unit_price)::numeric(12,0) AS revenue
FROM order_items oi JOIN products p ON p.id=oi.product_id JOIN categories c ON c.id=p.category_id
JOIN orders o ON o.id=oi.order_id WHERE o.status <> 'cancelled' GROUP BY c.name ORDER BY revenue DESC;

-- Q2: one customer's order history  (this one is the "slow" query we will fix)
SELECT o.id, o.status, o.created_at::date FROM orders o WHERE o.customer_id = 777 ORDER BY o.created_at DESC;

-- Q3: items of one order
SELECT p.name, oi.quantity, oi.unit_price FROM order_items oi JOIN products p ON p.id=oi.product_id WHERE oi.order_id = 4242;

-- Q4: top 5 customers by spend
SELECT c.name, SUM(pay.amount)::numeric(12,0) AS spent
FROM payments pay JOIN orders o ON o.id=pay.order_id JOIN customers c ON c.id=o.customer_id
GROUP BY c.name ORDER BY spent DESC LIMIT 5;
