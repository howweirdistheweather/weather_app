# HWITW web app
### Copyright (C) 2020 How weird is the weather developers

Note: you need to copy the sqlite database to this folder before building the image.
# cp ../../data/interim/lcd_daily.db .

create the docker image like so:
    docker build --tag hwitw .

run a docker container like so:
    docker run --rm --name hwitw-ctnr -p 5000:5000  hwitw


