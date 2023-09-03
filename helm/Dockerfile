# Dockerfile for HWITW
# Build from the root of the git repo with:
#     docker build -t ghcr.io/nceas/hwitw:0.9.0 -f helm/Dockerfile ./src
FROM python:3.9
WORKDIR /app
RUN groupadd -g 1004 datateam && useradd -m -u 1065 -g 1004 -s /bin/bash hwitw
COPY website/hwitw_requirements.txt .
COPY cdstotile/requirements.txt .
RUN pip install --upgrade -r hwitw_requirements.txt
RUN pip install --upgrade -r requirements.txt
USER hwitw:datateam
COPY ./website .
COPY ./cdstotile /cdstotile
ENV PORT 5000
CMD ["gunicorn", "--conf", "config.py", "--bind", "0.0.0.0:5000", "webapp:app"]
