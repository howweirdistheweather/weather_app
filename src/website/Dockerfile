# a docker image that packages up the HWITW server side web app
FROM python:3.7
# get the pip packages and other software installed first
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 --no-cache-dir install -r requirements.txt
# now copy the app/source into place. changes to src will build quickly this way.
COPY . /app
EXPOSE 5000
CMD ["python3", "./webapp.py"]
