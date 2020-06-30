#!/bin/bash
# docker image entrypoint for hwitw

# start postgres
sudo -u postgres pg_ctlcluster 11 main start

# start nginx
sudo nginx

# start gunicorn
exec gunicorn --workers 3 --bind unix:/app/wsgi.sock -m 000 wsgi:app 

# start webapp
#exec python3 ./webapp.py

