# Dockerfile for HWITW
# Build from the root of the git repo with:
#     nerdctl build -t ghcr.io/nceas/hwitw:0.7.0 -f helm/Dockerfile ./src
FROM python:3.9
WORKDIR /app
RUN groupadd -r hwitw && useradd -r -g hwitw hwitw
COPY website/hwitw_requirements.txt .
COPY cdstotile/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r hwitw_requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
USER hwitw:hwitw
COPY ./website .
COPY ./cdstotile /cdstotile
ENV PORT 5000
CMD ["gunicorn", "--conf", "config.py", "--bind", "0.0.0.0:5000", "webapp:app"]
