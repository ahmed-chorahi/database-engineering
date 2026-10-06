-- Users → Payments  (one-to-many) + a transaction
DROP DATABASE IF EXISTS pay;
CREATE DATABASE pay;
\c pay

CREATE TABLE users (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    balance NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (balance >= 0)
);

CREATE TABLE payments (
    id         SERIAL PRIMARY KEY,
    from_user  INT NOT NULL REFERENCES users(id),
    to_user    INT NOT NULL REFERENCES users(id),
    amount     NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (from_user <> to_user)
);

INSERT INTO users (name, balance) VALUES ('Ayesha', 500), ('Bilal', 100);

-- Pay 200 from Ayesha to Bilal: both updates or neither
BEGIN;
UPDATE users SET balance = balance - 200 WHERE id = 1;
UPDATE users SET balance = balance + 200 WHERE id = 2;
INSERT INTO payments (from_user, to_user, amount) VALUES (1, 2, 200);
COMMIT;
