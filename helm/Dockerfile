# Dockerfile for HWITW
# Build from the root of the git repo with:
#     nerdctl build -t hwitw-webapp:0.5.0 -f helm/Dockerfile ./src/website3
FROM python:3.9
WORKDIR /app
COPY hwitw_requirements.txt .
RUN pip install --no-cache-dir --upgrade -r hwitw_requirements.txt
COPY . .
ENV PORT 5000
CMD ["gunicorn", "--conf", "config.py", "--bind", "0.0.0.0:5000", "webapp:app"]
