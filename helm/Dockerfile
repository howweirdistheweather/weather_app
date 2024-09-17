# Dockerfile for HWITW
# Build from the root of the git repo with:
#     docker build -t ghcr.io/nceas/hwitw:1.0.0 -f helm/Dockerfile ./src
FROM python:3.11.6
LABEL org.opencontainers.image.source="https://github.com/howweirdistheweather/weather_app"
LABEL org.opencontainers.image.title="How Weird is the Weather (HWITW)"
LABEL org.opencontainers.image.version="0.9.8"
WORKDIR /app
RUN groupadd -g 1004 datateam && useradd -m -u 1065 -g 1004 -s /bin/bash hwitw
RUN apt update && apt install -y vim libhdf5-dev
COPY website/hwitw_requirements.txt .
COPY cdstotile/requirements.txt .
RUN pip install --upgrade -r hwitw_requirements.txt
RUN pip install --upgrade -r requirements.txt
COPY ./website .
COPY ./cdstotile /cdstotile
RUN chown -R hwitw . && chown -R hwitw /cdstotile
USER hwitw:datateam
ENV PORT=5000
CMD ["gunicorn", "--conf", "config.py", "--bind", "0.0.0.0:5000", "webapp:app"]
