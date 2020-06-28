#!/bin/bash
# docker image entrypoint for hwitw

# start postgres
sudo -u postgres pg_ctlcluster 11 main start

# start webapp
exec python3 ./webapp.py

