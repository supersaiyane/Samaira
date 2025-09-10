-- This init script runs automatically when the DB container is first created
\i /docker-entrypoint-initdb.d/schema.sql
