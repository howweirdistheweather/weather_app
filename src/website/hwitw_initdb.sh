#!/bin/sh
# initialize the HWITW database
sudo -u postgres psql -v ON_ERROR_STOP=1 --username "postgres" <<EOF
	CREATE USER hwitw WITH ENCRYPTED PASSWORD 'hwitw';
	CREATE DATABASE hwitw_lake;
	GRANT ALL PRIVILEGES ON DATABASE hwitw_lake to hwitw;
EOF

# create some tables
#psql -v ON_ERROR_STOP=1 postgresql://hwitw:hwitw@localhost/hwitw_lake?sslmode=require <<EOF
#	CREATE TABLE lcd_incoming;
#EOF

# load from backup
sudo -u postgres pg_restore --format c --dbname hwitw_lake  /app/hwitw_db_dump.bak

