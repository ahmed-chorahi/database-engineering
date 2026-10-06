DROP DATABASE IF EXISTS bank;
CREATE DATABASE bank;
\c bank
CREATE TABLE accounts (id INT PRIMARY KEY, owner TEXT, balance NUMERIC(10,2) CHECK (balance >= 0));
INSERT INTO accounts VALUES (1,'Ayesha',1000), (2,'Bilal',500);

CREATE TABLE seats (seat_no INT PRIMARY KEY, booked_by TEXT);
INSERT INTO seats VALUES (1, NULL), (2, NULL);

CREATE TABLE stock (product TEXT PRIMARY KEY, qty INT CHECK (qty >= 0));
INSERT INTO stock VALUES ('Laptop', 1);
