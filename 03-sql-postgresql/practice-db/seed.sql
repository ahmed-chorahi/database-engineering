\c shop

INSERT INTO customers (name, email, city, joined_on) VALUES
 ('Ayesha Khan', 'ayesha@mail.com', 'Islamabad', '2024-01-15'),
 ('Bilal Ahmed', 'bilal@mail.com',  'Lahore',    '2024-03-02'),
 ('Sara Malik',  'sara@mail.com',   'Karachi',   '2024-03-20'),
 ('Hamza Ali',   'hamza@mail.com',  'Lahore',    '2024-05-11'),
 ('Zainab Noor', NULL,              'Islamabad', '2024-06-01'),
 ('Usman Tariq', 'usman@mail.com',  NULL,        '2024-07-09');

INSERT INTO products (name, category, price) VALUES
 ('Laptop',          'Electronics', 950.00),
 ('Phone',           'Electronics', 600.00),
 ('Headphones',      'Electronics',  80.00),
 ('Desk',            'Furniture',   220.00),
 ('Chair',           'Furniture',   130.00),
 ('Notebook',        'Stationery',    3.50),
 ('Pen Pack',        'Stationery',    5.00),
 ('Backpack',        'Accessories',  45.00);

INSERT INTO orders (customer_id, order_date, status) VALUES
 (1, '2024-08-01', 'paid'),
 (1, '2024-08-15', 'shipped'),
 (2, '2024-08-03', 'paid'),
 (2, '2024-09-01', 'cancelled'),
 (3, '2024-08-20', 'shipped'),
 (4, '2024-09-05', 'pending'),
 (4, '2024-09-10', 'paid'),
 (1, '2024-09-12', 'paid');
-- Zainab (5) and Usman (6) have never ordered, on purpose.

INSERT INTO order_items (order_id, product_id, quantity) VALUES
 (1, 1, 1), (1, 3, 1),
 (2, 6, 10), (2, 7, 5),
 (3, 2, 1),
 (4, 4, 1),
 (5, 5, 2), (5, 8, 1),
 (6, 3, 2),
 (7, 1, 1), (7, 8, 2),
 (8, 6, 4);

INSERT INTO employees (name, dept, salary, manager_id) VALUES
 ('Omar',   'Management', 9000, NULL),
 ('Hina',   'Engineering', 6000, 1),
 ('Fahad',  'Engineering', 4500, 2),
 ('Mehwish','Engineering', 4800, 2),
 ('Rizwan', 'Sales',       4000, 1),
 ('Nida',   'Sales',       3500, 5),
 ('Talha',  'Sales',       3600, 5);
