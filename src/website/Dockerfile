# a docker image that packages up the HWITW server side web app
FROM python:3.7

# install packages
#RUN apt install postgresql-all

# do the pip install before copying all the source code files.
COPY hwitw_requirements.txt /app/hwitw_requirements.txt
WORKDIR /app
RUN pip3 --no-cache-dir install -r hwitw_requirements.txt

# install packages
RUN apt-get update && \
    apt-get install --no-install-recommends --yes sudo postgresql-11 bash && \
    apt-get clean

# init postgres db
COPY hwitw_initdb.sh hwitw_db_dump.bak /app/
RUN sudo -u postgres pg_ctlcluster 11 main start && \
    # initialize db
    /app/hwitw_initdb.sh && \
    # cleanly stop db
    sudo -u postgres pg_ctlcluster 11 main stop && \
    # done with the dbdump
    rm /app/hwitw_db_dump.bak

# fix postgres conf to allow any IP
RUN echo "listen_addresses='*'" >> /etc/postgresql/11/main/postgresql.conf
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/11/main/pg_hba.conf

# now copy everything else into place. changes to src will 'docker build' faster this way
# so we don't have to do all of the above everytime we change source code
COPY README.md hwitw_entrypoint.sh webauth.py webapp.py heatmap.py /app/
COPY templates /app/templates

# Expose the PostgreSQL port
EXPOSE 5432

# run the app server
EXPOSE 5000
CMD ["./hwitw_entrypoint.sh"]
