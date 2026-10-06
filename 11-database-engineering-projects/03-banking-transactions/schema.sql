DROP DATABASE IF EXISTS banking;
CREATE DATABASE banking;
\c banking

CREATE TABLE accounts (
    id      SERIAL PRIMARY KEY,
    owner   TEXT NOT NULL,
    balance NUMERIC(12,2) NOT NULL CHECK (balance >= 0)       -- overdraft impossible
);
CREATE TABLE transfers (
    id         SERIAL PRIMARY KEY,
    from_acct  INT NOT NULL REFERENCES accounts(id),
    to_acct    INT NOT NULL REFERENCES accounts(id),
    amount     NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (from_acct <> to_acct)
);
INSERT INTO accounts (owner, balance) SELECT 'Customer ' || g, 1000 FROM generate_series(1,5) g;
