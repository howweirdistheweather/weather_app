#!/bin/sh

export FLASK_APP=webapp.py
export FLASK_ENV=development
#sudo /home/duser/anaconda3/envs/hwitw/bin/flask run --host=0.0.0.0 --port=88
flask run --host=0.0.0.0 --port=5000
