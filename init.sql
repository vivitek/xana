CREATE USER xana WITH PASSWORD 'xana2020';
CREATE DATABASE xanadb;
GRANT ALL PRIVILEGES ON DATABASE xanadb TO xana;
GRANT pg_read_server_files TO xana;
