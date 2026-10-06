-- Least privilege demo. Run as a superuser:  psql -U postgres -d shop -f roles.sql
-- (needs the `shop` database from 03-sql-postgresql/practice-db)

DROP OWNED BY report_reader; DROP ROLE IF EXISTS report_reader;
DROP OWNED BY app_user;      DROP ROLE IF EXISTS app_user;

CREATE ROLE report_reader LOGIN PASSWORD 'change_me_1';   -- read-only analyst
CREATE ROLE app_user      LOGIN PASSWORD 'change_me_2';   -- the web app

GRANT CONNECT ON DATABASE shop TO report_reader, app_user;
GRANT USAGE   ON SCHEMA public TO report_reader, app_user;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_reader;
GRANT SELECT, INSERT, UPDATE ON orders, order_items TO app_user;
GRANT SELECT ON customers, products TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- take something back
REVOKE UPDATE ON orders FROM app_user;
