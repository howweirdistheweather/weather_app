# HWITW web app
### Copyright (C) 2020 How weird is the weather developers

create the docker image like so:
    docker build --tag hwitw .
    docker tag hwitw jamcinnes/hwitw

run a docker container like so:
    docker run --rm --name hwitw-ctnr -p 80:80 hwitw


